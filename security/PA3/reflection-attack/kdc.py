""" 
    Jake Pitkin - u0891770
    CS 6490 - Network Security
    Programming Assignment 3
"""

from socket import *
from Crypto import Random
from Crypto.Cipher import DES3
from Crypto.Util import Padding
import json

KDC_PORT = 12000

def main():
    """ Represents a KDC for the Needham Schroeder protocol. """
    print("Running Extended Needham Schroeder protocol.")
    print("--------------------------------------------")
    print()
    # User id to private key dictionary.
    kdc_registry = {}

    # Listen for users wanting to connect to the KDC.
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.bind(('', KDC_PORT))
    serv_sock.listen(1)

    while 1:
        # Incoming request.
        conn_sock, addr = serv_sock.accept()
        packet = conn_sock.recv(1024)
        request = json.loads(packet.decode('utf-8'))

        # Handle KDC key establishment requests.
        if request['type'] == "register":
            register_user(conn_sock, request['data'], kdc_registry)
        # Handle shared key generation requests.
        elif request['type'] == "key_establishment":
            create_shared_key(conn_sock, request, kdc_registry)
        else:
            raise Exception("Unknown request type.")


def register_user(conn_sock, user_id, registry):
    """ Attempts to register a new user in the KDC. Returns -1 if the user is already registered.

    Args:
        conn_sock (socket): User's socket.
        user_id (string): User's id in hexadecimal.
        registry (dict): Registry of registered users and their keys.

    Return:
        None.
    
    """
    # Check if the user is already registered with the KDC.
    if user_id in registry:
        print("User already registered with the KDC.")
        success = -1
        new_key = ""
    # If not, generate the user a new private key and store it with their ID.
    else:
        success = 1
        new_key = Random.get_random_bytes(16).hex()
    registry[user_id] = new_key
    response = { 'type' : "register",
                 'data' : new_key,
                 'success' : success }
    packet = json.dumps(response).encode('utf-8')
    print("Sending user their private key")
    print("KEY: {}".format(new_key))
    print()
    # Send the user their private key.
    conn_sock.send(packet)
    return


def create_shared_key(conn_sock, request, registry):
    """ Creates a shared key K_AB, extracts N_B, creates a ticket to Bob
        and sends this to Alice.

        Args:
            conn_sock (socket): Alice's socket.
            request (JSON): Request to the KDC from Alice.
            registry (dict): Dictionary of user ID -> private key.
        
        Return:
            None.
    """
    print("Generating shared key K_AB.")
    print()

    # Ensure both users are registered with the KDC.
    if request['alice_id'] not in registry:
        raise Exception("Recipient not registered with the KDC.")
    elif request['bob_id'] not in registry:
        raise Exception("Recipient not registered with the KDC.")

    BOB_ID = request['bob_id']
    ALICE_ID = request['alice_id']
    K_B = registry[BOB_ID]
    K_A = registry[ALICE_ID]
    # Extract Bob's nonce.
    N_B = decrypt_plaintext(K_B, request['enc_N_B'])
    # Generate a shared key for Alice and Bob.
    K_AB = Random.get_random_bytes(16).hex()
    print("Generating shared key K_AB.")
    print("K_AB: {}".format(K_AB))
    # Generate a nonce N_1.
    N_1 = request['nonce']
    # Create a response for Alice.
    ticket_package = create_ticket_package(ALICE_ID, BOB_ID, K_AB, K_A, K_B, N_B, N_1)
    print("Creating ticket to Bob package.")
    print("PACKAGE: {}".format(ticket_package))
    print()
    response = { 'type' : "key_establishment", 
                 'data' : ticket_package }        
    # Send response to Alice.
    packet = json.dumps(response).encode('utf-8')
    print("Sending Alice ticket to Bob package.")
    conn_sock.send(packet)
    return


def create_ticket_package(ALICE_ID, BOB_ID, K_AB, K_A, K_B, N_B, N_1):
    """ Creates the ticket package to respond to Alice.
        K_A{N_1, BOB_ID, K_AB, K_B{K_AB, ALICE_ID, N_B}}

        Return:
            ticket_package (hex): hex string representing the ticket package.
    """

    ticket_to_bob = K_AB + ALICE_ID + N_B
    ticket_to_bob = encrypt_plaintext(K_B, ticket_to_bob)
    ticket_package = N_1 + BOB_ID + K_AB + ticket_to_bob
    ticket_package = encrypt_plaintext(K_A, ticket_package)
    return ticket_package


def encrypt_plaintext(key, plaintext):
    """ Encrypts plaintext with the given key and appends the iv to the front.

        Args:
            key (hex): DES3 key.
            plaintext (hex): unpadded plaintext.

        Return:
            ciphertext (hex): padded encrypted plaintext with the iv appended to the front.
    """

    key = bytes.fromhex(key)
    plaintext = bytes.fromhex(plaintext)
    iv = Random.new().read(DES3.block_size)
    des3 = DES3.new(key, DES3.MODE_CBC, iv)
    ciphertext = des3.encrypt(Padding.pad(plaintext, DES3.block_size))
    ciphertext = (iv + ciphertext).hex()
    return ciphertext


def decrypt_plaintext(key, ciphertext):
    """ Assumes the iv is appended to the front of the ciphertext and is 8 bytes.
        
        Args:
            key (hex): DES3 key.
            ciphertext (hex): padded ciphertext with the iv appened to the front.
        
        Return:
            unpadded_plaintext (hex): decrypted plaintext.
    """

    key = bytes.fromhex(key)
    ciphertext = bytes.fromhex(ciphertext)
    iv = ciphertext[0:8]
    des3 = DES3.new(key, DES3.MODE_CBC, iv)
    plaintext = des3.decrypt(ciphertext[8:])
    unpadded_plaintext = Padding.unpad(plaintext, DES3.block_size)
    return unpadded_plaintext.hex()


if __name__ == "__main__":
    main()
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
BOB_PORT = 12001
ALICE_PORT = 12002

def main():
    """ Executes the extended-NS protocol with Bob.
        Alice is the party that contacts the KDC. 
    """
    print("Running Original Needham Schroeder protocol.")
    print("--------------------------------------------")
    print()

    # Generate a unique ID and register with the KDC.
    ALICE_ID = Random.get_random_bytes(8).hex()
    write_id(ALICE_ID)
    BOB_ID = read_id()
    K_A = register_with_kdc(ALICE_ID)

    # Contact the KDC to get K_AB and the ticket to Bob.
    N_1 = Random.get_random_bytes(8).hex()
    kdc_response = contact_kdc(ALICE_ID, BOB_ID, N_1)

    # Deconstruct the response from the KDC.
    ticket, K_AB = deconstruct_kdc_response(kdc_response, K_A, N_1, BOB_ID)

    # Send Bob his ticket and a new nonce encrypted with the shared key.
    N_2 = Random.get_random_bytes(8).hex()
    send_bob_ticket(ticket, K_AB, N_2)

    # Wait for Bob to respond with his challenge.
    N_3 = wait_for_bob_challenge(K_AB, N_2)

    # Send final challenge K_AB{N_3 - 1} to Bob.
    final_challenge(K_AB, N_3)


def final_challenge(K_AB, N_3):
    """ Send the final challenge K_AB{N_3 - 1} to Bob to authenticate Alice. """
    
    # Calculate N_3 - 1.
    N_3_1 = hex(int(N_3, 16) - 1)[2:] 
    print("Sending challenge K_AB{{N_3 - 1}} to Bob.")
    print("K_AB: {}".format(K_AB))
    print("N_3 - 1: {}".format(N_3_1))
    challenge = encrypt_plaintext(K_AB, N_3_1)
    request = { 'challenge' : challenge }
    # Send K_AB{N_3 - 1} to Bob.
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', BOB_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    print()
    print("FINISHED: Fully authenicated with Bob and K_AB exchanged.")
    return


def wait_for_bob_challenge(K_AB, N_2):
    """ Listen for Bob to send challenge K_AB{N_2 - 1, N_3} 
        Throws an exception if N_2 - 1 does not match. """

    # Setup a socket to listen for Bob.
    alice_lis_sock = socket(AF_INET, SOCK_STREAM)
    alice_lis_sock.bind(('', ALICE_PORT))
    alice_lis_sock.listen(1)
    bob_sock, addr = alice_lis_sock.accept()
    request = bob_sock.recv(1024)
    request = json.loads(request)
    print("Received Bob's challenge K_AB{{N_2 - 1, N_3}}")
    print("K_AB: {}".format(K_AB))
    print("K_AB{{N_2 - 1, N_3}}: {}".format(request['challenge']))
    # Decrypt K_AB{N_2 - 1, N_3}
    plaintext = decrypt_plaintext(K_AB, request['challenge'])
    print("(N_2 - 1, N_3): {}".format(plaintext))
    N_2_1 = plaintext[0:16]
    N_3 = plaintext[16:32]
    print("N_2 - 1: {}".format(N_2_1))
    print("N_3: {}".format(N_3))
    print()
    # Verify N_2 - 1
    if hex(int(N_2, 16) - 1)[2:] != N_2_1:
        raise Exception("Challenge N_2 - 1 does not match.")
    return N_3


def send_bob_ticket(ticket, K_AB, N_2):
    """ Sends Bob his ticket and challange K_AB{N_2} """

    print()
    print("Sending Bob the ticket and K_AB{{N_2}}.")
    print("K_AB: {}".format(K_AB))
    print("N_2: {}".format(N_2))
    # Encrypt N_2 with K_AB.
    encrypted_nonce = encrypt_plaintext(K_AB, N_2)
    print("K_AB{{N_2}}: {}".format(encrypted_nonce))
    print()
    request = { 'ticket' : ticket,
                'nonce' : encrypted_nonce }
    # Send Bob his ticket and the encrypted challenge.
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', BOB_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    return


def deconstruct_kdc_response(kdc_response, K_A, N_1, BOB_ID):
    """ Decrypts the response from the KDC and deconstructs it
        into it's respective parts.
        Throws an exception if BOB_ID or N_1 do not match.
    """

    print()
    print("Deconstructing KDC response into it's parts.")
    # Decrypt the response from the KDC.
    plaintext = decrypt_plaintext(K_A, kdc_response)
    nonce = plaintext[0:16]
    bob = plaintext[16:32]    
    K_AB = plaintext[32:64]
    ticket = plaintext[64:]
    # Verify BOB_ID and N_1.
    if N_1 != nonce:
        raise Exception("Nonce N_1 does not match.")
    if BOB_ID != bob:
        raise Exception("Bob's ID does not match.")
    return ticket, K_AB


def contact_kdc(ALICE_ID, BOB_ID, N_1):
    """ Contact the KDC to get shared key K_AB and ticket to Bob. """
    
    request = { 'type' : "key_establishment",
                'alice_id' : ALICE_ID, 
                'bob_id' : BOB_ID,
                'nonce' : N_1 }
    # Send request to the KDC.
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', KDC_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    print("Requesting K_AB from the KDC.")
    print("N_1: {}".format(N_1))
    print("ALICE_ID: {}".format(ALICE_ID))
    print("BOB_ID: {}".format(BOB_ID))
    # Receive response from the KDC.
    response = sock.recv(1024)
    response = json.loads(response)
    if response['type'] != "key_establishment":
        raise Exception("Expected key establishment from the KDC.")
    print("Received ticket to Bob package from KDC.")
    return response['data']


def register_with_kdc(id):
    """ Registers a unique ID with the KDC and a unique private key is received if the user isn't already registered. 
    
    Args:
        id (string): Unique id in hexadecimal.

    Return:
        private_key (hex): Generated private key.

    """
    
    request = { 'type' : "register",
                'data' : id }
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', KDC_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    response = sock.recv(1024)
    response = json.loads(response)
    private_key = response['data']
    if response['success'] == -1:
        raise Exception("ID already registered with the KDC.")
    print("Registered with the KDC.")
    print("K_A: {}".format(private_key))
    print()
    return private_key


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
    des3 = DES3.new(key, DES3.MODE_ECB)
    ciphertext = des3.encrypt(Padding.pad(plaintext, DES3.block_size))
    return ciphertext.hex()


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
    des3 = DES3.new(key, DES3.MODE_ECB)
    plaintext = des3.decrypt(ciphertext)
    unpadded_plaintext = Padding.unpad(plaintext, DES3.block_size)
    return unpadded_plaintext.hex()



def write_id(id):
    with open("alice.txt", 'w') as f:
        f.write(id)


def read_id():
    with open("bob.txt", 'r') as f:
        lines = f.readlines()
    return lines[0]


if __name__ == "__main__":
    main()
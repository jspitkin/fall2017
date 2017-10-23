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
    """ Executes the extended-NS protocol with Alice.
        Bob is the party that does not contact the KDC. 
    """
    print("Running Original Needham Schroeder protocol.")
    print("--------------------------------------------")
    print()

    #Generate a unique ID and register with the KDC.
    BOB_ID = Random.get_random_bytes(8).hex()
    write_id(BOB_ID)
    K_B = register_with_kdc(BOB_ID)

    # Setup a socket for Bob to listen on.
    bob_lis_sock = socket(AF_INET, SOCK_STREAM)
    bob_lis_sock.bind(('', BOB_PORT))
    bob_lis_sock.listen(1)

    # Wait for Alice to contact me with a ticket.
    K_AB, N_2 = wait_for_ticket(bob_lis_sock, K_B)

    # Send challenge K_AB{N_2 - 1, N_3} to Alice.
    N_3 = Random.get_random_bytes(8).hex()
    send_alice_challenge(K_AB, N_2, N_3)

    # Wait for Alice's response to challenge K_AB{N_3 - 1}.
    wait_for_alice_response(K_AB, N_3, bob_lis_sock)


def wait_for_alice_response(K_AB, N_3, bob_lis_sock):
    """ Wait for Alice to respond to challenge K_AB{N_3 - 1}.
        Throws an exception if challenge does not match.
    """

    # Listen for Alice to respond to the challenge.
    alice_sock, addr = bob_lis_sock.accept()
    request = alice_sock.recv(1024)
    request = json.loads(request)
    # Decrypt the challenge
    N_3_1 = decrypt_plaintext(K_AB, request['challenge'])
    # Check the challenge.
    if N_3_1 != hex(int(N_3, 16) - 1)[2:]:
        raise Exception("Challenge N_3 - 1 does not match.")
    print()
    print("N_3 - 1: {}".format(N_3_1))
    print("FINISHED: Fully authenticated with Alice and K_AB exchanged.")
    return


def send_alice_challenge(K_AB, N_2, N_3):
    """ Send Alice the challenge K_AB{N_2 - 1, N_3}. """
    
    # Calculate N_2 - 1.
    N_2_1 = hex(int(N_2, 16) - 1)[2:]
    # Encrypt the challenge.
    challenge = encrypt_plaintext(K_AB, N_2_1 + N_3)
    response = { 'challenge' : challenge }
    packet = json.dumps(response).encode('utf-8')
    # Send the challenge to Alice.
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', ALICE_PORT))
    sock.send(packet)
    print("Sending Alice challenge K_AB{{N_2 - 1, N_3}}.")
    print("K_AB{{N_2 - 1, N_3}}: {}".format(challenge))
    print("K_AB: {}".format(K_AB))
    print("N_2 - 1: {}".format(N_2_1))
    print("N_3: {}".format(N_3))
    print()
    return


def wait_for_ticket(bob_lis_sock, K_B):
    """ Wait for Alice to respond with the ticket to Bob.
        Exception is thrown if ALICE_ID does not match expected value.
    """

    # Listen for Alice to send ticket to Bob.
    alice_sock, addr = bob_lis_sock.accept()
    request = alice_sock.recv(1024)
    request = json.loads(request)
    # Decrypt the ticket to Bob.
    ALICE_ID = read_id()
    encrypted_ticket = request['ticket']
    ticket = decrypt_plaintext(K_B, encrypted_ticket)
    K_AB = ticket[0:32]
    alice_id = ticket[32:48]
    print("Received ticket and K_AB{{N_2}} from Alice.")
    print("Encrypted ticket: {}".format(encrypted_ticket))
    print("Decrypted ticket: {}".format(ticket))
    print("K_AB: {}".format(K_AB))
    print("K_AB{{N_2}}: {}".format(request['nonce']))
    # Verify ALICE_ID.
    if ALICE_ID != alice_id:
        raise Exception("Alice's ID does not match.")
    encrypted_N_2 = request['nonce']
    N_2 = decrypt_plaintext(K_AB, encrypted_N_2)
    print("N_2: {}".format(N_2))
    print()
    return K_AB, N_2



def register_with_kdc(id):
    """ Registers a unique ID with the KDC and a unique private key is received if the user isn't already registered. 
    
    Args:
        id (string): Unique id in hexadecimal.
        kdc_port (int): KDC's port.

    Return:
        private_key (byte): Generated private key.

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
        print("ID already registered with the KDC.")
        return ""
    print("Registered with the KDC.")
    print("K_B: {}".format(private_key))
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
    with open("bob.txt", 'w') as f:
        f.write(id)


def read_id():
    with open("alice.txt", 'r') as f:
        lines = f.readlines()
    return lines[0]

if __name__ == "__main__":
    main()

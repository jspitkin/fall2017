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
TRUDY_PORT = 12003

def main():
    """ Executes the extended-NS protocol with Alice.
        Bob is the party that does not contact the KDC. 
    """
    # Run Bob before Trudy
    print("Running Original Needham Schroeder protocol.")
    print("--------------------------------------------")
    print()

    #Generate a unique ID and register with the KDC.
    BOB_ID = Random.get_random_bytes(8).hex()
    K_B = Random.get_random_bytes(16).hex() 
    write(K_B, "KB.txt")

    # Setup a socket for Bob to listen on.
    bob_lis_sock = socket(AF_INET, SOCK_STREAM)
    bob_lis_sock.bind(('', BOB_PORT))
    bob_lis_sock.listen(1)

    # Wait for Trudy to contact me with a ticket.
    K_AB, N_2 = wait_for_ticket(bob_lis_sock, K_B)

    # Send Trudy K_AB{N_2 - 1, N_4}.
    N_4 = send_trudy_challenge_1(K_AB, N_2)

    # Wait for Trudy to contact me with a ticket on a second connection.
    wait_for_ticket_2(bob_lis_sock, K_B)

    # Send Trudy K_AB{N_4 - 1, N_5}
    send_trudy_challenge_2(K_AB, N_4)

    # Wait for Trudy to respond with K_AB{N_4 - 1}.
    wait_for_trudy_response(K_AB, N_4, bob_lis_sock)


def wait_for_trudy_response(K_AB, N_4, bob_lis_sock):
    """ Wait for Trudy to respond with challenge K_AB{N_4 - 1}.
        Throws an exception if challenge does not match.
    """

    # Listen for Alice to respond to the challenge.
    trudy_sock, addr = bob_lis_sock.accept()
    request = trudy_sock.recv(1024)
    request = json.loads(request)
    # Check the challenge.
    expected = encrypt_plaintext(K_AB, hex(int(N_4, 16) - 1)[2:])
    if request['challenge'][0:16] != expected[0:16]:
        raise Exception("Challenge N_4 - 1 does not match.")
    print("Expected: {}".format(expected[0:16]))
    print("Trudy response to challenge: {}".format(request['challenge'][0:16]))
    print()
    print("FINISHED: Fully authenticated with Trudy with Bob.")
    print("Bob thinks Trudy is Alice.")
    return


def send_trudy_challenge_1(K_AB, N_2):
    """ Send Alice (Trudy) the challenge K_AB{N_2 - 1, N_4}. """
    
    # Calculate N_2 - 1.
    N_2_1 = hex(int(N_2, 16) - 1)[2:]
    N_4 = Random.get_random_bytes(8).hex()
    # Encrypt the challenge.
    challenge = encrypt_plaintext(K_AB, N_2_1 + N_4)
    response = { 'challenge' : challenge }
    packet = json.dumps(response).encode('utf-8')
    # Send the challenge to Alice.
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', TRUDY_PORT))
    sock.send(packet)
    sock.close()
    print("Sending Trudy challenge K_AB{{N_2 - 1, N_4}}.")
    print("K_AB{{N_2 - 1, N_4}}: {}".format(challenge))
    print("K_AB: {}".format(K_AB))
    print("N_2 - 1: {}".format(N_2_1))
    print("N_4: {}".format(N_4))
    print()
    return N_4


def send_trudy_challenge_2(K_AB, N_4):
    """ Send Alice (Trudy) the challenge K_AB{N_4 - 1, N_5}. """
    
    # Calculate N_2 - 1.
    N_4_1 = hex(int(N_4, 16) - 1)[2:]
    N_5 = Random.get_random_bytes(8).hex()
    # Encrypt the challenge.
    challenge = encrypt_plaintext(K_AB, N_4_1 + N_4)
    response = { 'challenge' : challenge }
    packet = json.dumps(response).encode('utf-8')
    # Send the challenge to Alice.
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', TRUDY_PORT))
    sock.send(packet)
    print("Sending Trudy challenge K_AB{{N_4 - 1, N_5}}.")
    print("K_AB{{N_4 - 1, N_5}}: {}".format(challenge))
    print("K_AB: {}".format(K_AB))
    print("N_4 - 1: {}".format(N_4_1))
    print("N_5: {}".format(N_5))
    print()
    return


def wait_for_ticket(bob_lis_sock, K_B):
    """ Wait for Alice to respond with the ticket to Bob.
        Exception is thrown if ALICE_ID does not match expected value.
    """

    # Listen for Alice to send ticket to Bob.
    print()
    alice_sock, addr = bob_lis_sock.accept()
    request = alice_sock.recv(1024)
    request = json.loads(request)
    # Decrypt the ticket to Bob.
    ALICE_ID = read("alice.txt")
    encrypted_ticket = request['ticket']
    ticket = decrypt_plaintext(K_B, encrypted_ticket)
    K_AB = ticket[0:32]
    alice_id = ticket[32:48]
    print("Received ticket and K_AB{{N_2}} from Trudy.")
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


def wait_for_ticket_2(bob_lis_sock, K_B):
    """ Wait for Alice to respond with the ticket to Bob.
        Exception is thrown if ALICE_ID does not match expected value.
    """

    # Listen for Alice to send ticket to Bob.
    trudy_sock, addr = bob_lis_sock.accept()
    request = trudy_sock.recv(1024)
    request = json.loads(request)
    # Decrypt the ticket to Bob.
    encrypted_ticket = request['ticket']
    ticket = decrypt_plaintext(K_B, encrypted_ticket)
    K_AB = ticket[0:32]
    alice_id = ticket[32:48]
    print("Received ticket and K_AB{{N_4}} from Trudy.")
    print("Encrypted ticket: {}".format(encrypted_ticket))
    print("Decrypted ticket: {}".format(ticket))
    print("K_AB: {}".format(K_AB))
    print("K_AB{{N_4}}: {}".format(request['nonce']))
    encrypted_N_4 = request['nonce']
    #N_4 = decrypt_plaintext(K_AB, request['nonce'])
    #print("N_4: {}".format(N_4))
    print()
    return


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


def write(value, path):
    with open(path, 'w') as f:
        f.write(value)


def read(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    return lines[0]

if __name__ == "__main__":
    main()

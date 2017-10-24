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

BOB_PORT = 12001
TRUDY_PORT = 12003

def main():
    """ Trudy causing a reflection attack against the original-NS protocol.
        Assume Trudy has sniffed messages 3 and 4 of Alice and Bob's protocol.
    """

    print("Running Original Needham Schroeder protocol.")
    print("--------------------------------------------")
    print()
    ticket, encrypt_N_2, message_4 = get_message_3_and_4()

    # Send Bob the intercepted message 3.
    send_bob_ticket(ticket, encrypt_N_2)

    # Listen for Bob's response K_AB{N_2 - 1, N_4}.
    challenge = listen_for_challenge()

    # Slice out K_AB{N_4}.
    print("Slicing out K_AB{{N_4}}.")
    encrypt_N_4 = challenge[24:48]

    # Open a new connection with Bob and send ticket K_AB{N_4}.
    send_bob_ticket_2(ticket, encrypt_N_4)

    # Listen for response K_AB{N_4 - 1, N_5}.
    challenge = listen_for_challenge()

    # Slice out K_AB{N_4 - 1}
    print("Slicing out K_AB{{N_4 - 1}}")
    encrypt_N_4_1 = challenge[0:24]
    print("K_AB{{N_4 - 1}}: {}".format(encrypt_N_4_1))
    print()
    
    # Respond with K_AB{N_4 - 1} in first connection.
    send_bob_challenge_first_connection(encrypt_N_4_1)

def send_bob_challenge_first_connection(encrypt_N_4_1):
    print("Sending Bob K_AB{{N_4 - 1}} on initial connection.")
    print("K_AB{{N_4 - 1}}: {}".format(encrypt_N_4_1))
    print()
    request = { 'challenge' : encrypt_N_4_1 }
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', BOB_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    return


def listen_for_challenge():
    trudy_lis_sock = socket(AF_INET, SOCK_STREAM)
    trudy_lis_sock.bind(('', TRUDY_PORT))
    trudy_lis_sock.listen(1)

    bob_sock, addr = trudy_lis_sock.accept()
    request = bob_sock.recv(1024)
    request = json.loads(request)
    return request['challenge']


def get_intercepted_message():
    print("Trudy intercepts K_AB{{N_2 - 1, N_4}}.")
    K_AB = read("KAB.txt")
    N_2 = read("N2.txt")
    N_2_1 = hex(int(N_2, 16) - 1)[2:]
    N_4 = Random.get_random_bytes(8).hex()
    message = encrypt_plaintext(K_AB, N_2_1 + N_4)
    return message


def send_bob_ticket(ticket, encrypt_N_2):
    """ Sends Bob his ticket and challange K_AB{N_2} """

    print()
    print("Sending Bob the sniffed ticket and K_AB{{N_2}}.")
    print("K_AB{{N_2}}: {}".format(encrypt_N_2))
    print("Ticket to Bob: {}".format(ticket))
    print()
    request = { 'ticket' : ticket,
                'nonce' : encrypt_N_2 }
    # Send Bob his ticket and the encrypted challenge.
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', BOB_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    return


def send_bob_ticket_2(ticket, encrypt_N_4):
    """ Sends Bob his ticket and challange K_AB{N_2} """

    print()
    print("Sending Bob the sniffed ticket and K_AB{{N_4}}.")
    print("K_AB{{N_4}}: {}".format(encrypt_N_4))
    print("Ticket to Bob: {}".format(ticket))
    print()
    request = { 'ticket' : ticket,
                'nonce' : encrypt_N_4 }
    # Send Bob his ticket and the encrypted challenge.
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', BOB_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    return


def get_message_3_and_4():
    """ Mocking Trudy sniffing message 3 and 4 of Alice and Bob's communication. """

    print("Messages 3 and 4 intercepted by Trudy!")
    ALICE_ID = read("alice.txt")
    K_AB = Random.get_random_bytes(16).hex()
    write(K_AB, "KAB.txt")
    K_B = read("KB.txt")
    N_2 = Random.get_random_bytes(8).hex()
    write(N_2, "N2.txt")
    N_2_1 = hex(int(N_2, 16) - 1)[2:]
    N_3 = Random.get_random_bytes(8).hex()
    encrypt_N_2 = encrypt_plaintext(K_AB, N_2)
    ticket = encrypt_plaintext(K_B, K_AB + ALICE_ID)
    message_4 = encrypt_plaintext(K_AB, N_2_1 + N_3)
    print("Ticket to Bob: {}".format(ticket))
    print("K_AB{{N_2}}: {}".format(encrypt_N_2))
    print("K_AB{{N_2 - 1, N_3}}: {}".format(message_4))
    print()
    return ticket, encrypt_N_2, message_4
    

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


def read(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    return lines[0]


def write(value, path):
    with open(path, 'w') as f:
        f.write(value)


if __name__ == "__main__":
    main()
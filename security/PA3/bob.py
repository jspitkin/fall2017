from socket import *
from Crypto import Random
from Crypto.Cipher import DES3
from Crypto.Util import Padding
import json

KDC_PORT = 12000
BOB_PORT = 12001
ALICE_PORT = 12002

def main():
    #Generate a unique ID and register with the KDC.
    BOB_ID = Random.get_random_bytes(8).hex()
    K_B = register_with_kdc(BOB_ID)

    # Setup a socket for Bob to listen on.
    bob_lis_sock = socket(AF_INET, SOCK_STREAM)
    bob_lis_sock.bind(('', BOB_PORT))
    bob_lis_sock.listen(1)

    # Wait for Alice to initially contact me.
    ALICE_ID, N_B, alice_sock = wait_for_alice(BOB_ID, K_B, bob_lis_sock)

    # Wait for Alice to  contact me with a ticket.
    K_AB, N_2 = wait_for_ticket(bob_lis_sock, K_B, ALICE_ID, N_B)

    # Send challenge K_AB{N_2 - 1, N_3} to Alice.
    N_3 = Random.get_random_bytes(8).hex()
    send_alice_challenge(K_AB, N_2, N_3, alice_sock)

    # Wait for Alice's response to challenge K_AB{N_3 - 1}.
    wait_for_alice_response(K_AB, N_3, bob_lis_sock)


def wait_for_alice_response(K_AB, N_3, bob_lis_sock):
    alice_sock, addr = bob_lis_sock.accept()
    request = alice_sock.recv(1024)
    request = json.loads(request)
    N_3_1 = decrypt_plaintext(K_AB, request['challenge'])
    if N_3_1 != hex(int(N_3, 16) - 1)[2:]:
        raise Exception("Challenge N_3 - 1 does not match.")
    print()
    print("FINISHED: Fully authenticated with Alice and K_AB exchanged.")


def send_alice_challenge(K_AB, N_2, N_3, alice_sock):
    N_2_1 = hex(int(N_2, 16) - 1)[2:]
    challenge = encrypt_plaintext(K_AB, N_2_1 + N_3)
    response = { 'challenge' : challenge }
    packet = json.dumps(response).encode('utf-8')
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', ALICE_PORT))
    sock.send(packet)
    print("Sending Alice challenge K_AB{{N_2 - 1, N_3}}.")
    return
    

def wait_for_alice(BOB_ID, K_B, bob_lis_sock):
    """ Wait for Alice to make initial contact. When she does, encrypt a nonce N_B with K_BOB and send it to Alice.
    """
    
    alice_sock, addr = bob_lis_sock.accept()
    request = alice_sock.recv(1024)
    request = json.loads(request)
    if request['type'] != "initial":
        raise Exception("Expected Alice's initial message.")    
    print("Received Alice's initial communication message.")
    print()
    N_B = Random.get_random_bytes(8)
    key = bytes.fromhex(K_B)
    iv = Random.new().read(DES3.block_size)
    des3 = DES3.new(key, DES3.MODE_CBC, iv)
    encrypted_N_B = des3.encrypt(Padding.pad(N_B, DES3.block_size))
    encrypted_N_B = (iv + encrypted_N_B).hex()
    response = { 'type' : "initial",
                 'sender_id' : BOB_ID,
                 'data' : encrypted_N_B }
    packet = json.dumps(response).encode('utf-8')
    print("Sending Alice encrypted nonce K_B{{N_B}}")
    print()
    alice_sock.send(packet)
    return request['sender_id'], N_B.hex(), alice_sock


def wait_for_ticket(bob_lis_sock, K_B, ALICE_ID, N_B):
    alice_sock, addr = bob_lis_sock.accept()
    request = alice_sock.recv(1024)
    request = json.loads(request)
    print("Received ticket and K_AB{{N_2}} from Alice.")
    print()
    encrypted_ticket = request['ticket']
    ticket = decrypt_plaintext(K_B, encrypted_ticket)
    K_AB = ticket[0:32]
    alice_id = ticket[32:48]
    n_b = ticket[48:64]
    if ALICE_ID != alice_id:
        raise Exception("Alice's ID does not match.")
    if N_B != n_b:
        raise Exception("Nonce N_B does not match.")
    encrypted_N_2 = request['nonce']
    N_2 = decrypt_plaintext(K_AB, encrypted_N_2)
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

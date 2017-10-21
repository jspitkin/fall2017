from socket import *
from Crypto import Random
from Crypto.Cipher import DES3
import json

KDC_PORT = 12000
BOB_PORT = 12001

def main():
    # Generate a unique ID and register with the KDC
    BOB_ID = Random.get_random_bytes(8).hex()
    K_B = register_with_kdc(BOB_ID)

    bob_lis_sock = socket(AF_INET, SOCK_STREAM)
    bob_lis_sock.bind(('', BOB_PORT))
    bob_lis_sock.listen(1)

    # Wait for Alice to initially contact me.
    ALICE_ID = wait_for_alice(BOB_ID, K_B, bob_lis_sock)

    # Wait for Alice to  contact me with a ticket.
    wait_for_ticket()
    

def wait_for_alice(BOB_ID, K_B, bob_lis_sock):
    """ Wait for Alice to make initial contact. When she does, encrypt a nonce N_B with K_BOB and send it to Alice.
    """
    
    alice_sock, addr = bob_lis_sock.accept()
    request = alice_sock.recv(1024)
    request = json.loads(request)
    if request['type'] != "initial":
        raise Exception("Expected Alice's initial message.")    
    print("Received Alice's initial message.")
    N_B = Random.get_random_bytes(8)
    key = DES3.adjust_key_parity(bytes.fromhex(K_B))
    cipher = DES3.new(key, DES3.MODE_CFB)
    encrypted_N_B = cipher.encrypt(N_B).hex()
    response = { 'type' : "initial",
                 'sender_id' : BOB_ID,
                 'data' : encrypted_N_B }
    packet = json.dumps(response).encode('utf-8')
    print("Sending Alice an encrypted nonce {}".format(encrypted_N_B))
    print()
    alice_sock.send(packet)
    return request['sender_id']


def wait_for_ticket():
    lis_sock = socket(AF_INET, SOCK_STREAM)
    lis_sock.bind(('', BOB_PORT))
    lis_sock.listen(1)
    alice_sock, addr = lis_sock.accept()
    request = alice_sock.recv(1024)
    request = json.loads(request)


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
    print("Registered with the KDC with key {}".format(private_key))
    print()
    return private_key


if __name__ == "__main__":
    main()

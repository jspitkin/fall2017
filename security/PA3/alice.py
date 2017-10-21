from socket import *
from Crypto import Random
import json

KDC_PORT = 12000
BOB_PORT = 12001

def main():
    # Generate a unique ID and register with the KDC
    ALICE_ID = Random.get_random_bytes(8).hex()
    K_A = register_with_kdc(ALICE_ID)

    # Initiate contact with Bob.
    BOB_ID, encrypted_N_B = initiate_contact_bob(ALICE_ID)

    # Contact the KDC to get K_AB and the ticket to Bob
    kdc_response = contact_kdc(ALICE_ID, BOB_ID, encrypted_N_B)


def initiate_contact_bob(ALICE_ID):
    """ Initiate contact with Bob to begin the Needham-Schroeder protocol.
    """

    request = { 'type' : "initial",
                'sender_id' : ALICE_ID,
                'data' : "I want to talk to you" }
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', BOB_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    response = sock.recv(1024)
    response = json.loads(response)
    if response['type'] != "initial":
        raise Exception("Expected Bob's initial message.")
    encrypted_nonce = response['data']
    BOB_ID = response['sender_id']
    print("Received Bob's initial encrypted nonce {}".format(encrypted_nonce))
    print()
    return BOB_ID, encrypted_nonce


def contact_kdc(req_id, rec_id, encrypted_N_B):
    N_1 = Random.get_random_bytes(8).hex()
    request = { 'type' : "initial",
                'requester_id' : req_id, 
                'recipient_id' : rec_id,
                'nonce' : N_1,
                'enc_N_B' : encrypted_N_B }


def register_with_kdc(id):
    """ Registers a unique ID with the KDC and a unique private key is received if the user isn't already registered. 
    
    Args:
        id (string): Unique id in hexadecimal.

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
        raise Exception("ID already registered with the KDC.")
    print("Registered with the KDC with key {}".format(private_key))
    print()
    return private_key


if __name__ == "__main__":
    main()
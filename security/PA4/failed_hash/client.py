"""
    Jake Pitkin - u0891770
    CS 6490 - Fall 2017
    Programming Assignment 4
"""

from socket import *
from Crypto import Random
from Crypto.Hash import SHA1
from OpenSSL import crypto
import json
import util

CLIENT_PORT = 12000
SERVER_PORT = 12001
CLIENT_CERT_PATH = "client.crt"
CLIENT_KEY_PATH = "client.key"
handshake_messages = ""


def main():
    global handshake_messages
    # Create a certificate and key pair for the client.
    util.create_certificate_and_key(CLIENT_CERT_PATH, CLIENT_KEY_PATH)

    # Generate R_CLIENT and read the client's certificate from file.
    R_CLIENT = Random.get_random_bytes(32).hex()
    print()
    print("Creating R_CLIENT.")
    print("R_CLIENT: {}".format(R_CLIENT))
    print()
    client_cert = util.read_certificate(CLIENT_CERT_PATH)

    # Message 1 - initial contact with Bob
    response = initial_contact(R_CLIENT, client_cert)

    # Extract the server's nonce.
    server_cert = crypto.load_certificate(crypto.FILETYPE_PEM, response['cert'])
    cert_print = crypto.dump_certificate(crypto.FILETYPE_PEM, server_cert).decode()
    client_priv_key = util.get_private_key(CLIENT_KEY_PATH)
    R_SERVER = util.rsa_decrypt(bytes.fromhex(response['nonce']), client_priv_key).hex()
    print()
    print("Received initial response from the server.")
    print("C_PUB{{R_SERVER}} {}".format(response['nonce']))
    print("R_SERVER: {}".format(R_SERVER))
    print()
    print("Server SSL Certificate:\n {}".format(cert_print))
    print()

    # Generate the master secret.
    K = util.generate_master_secret(R_CLIENT, R_SERVER)
    print("Creating master key from R_CLIENT and R_SERVER.")
    print("K: {}".format(K))
    print()


    # Compute the hash of the handshake messages.
    handshake_messages += K
    sha1_hasher = SHA1.new()
    sha1_hasher.update(("CLIENT" + handshake_messages).encode('utf-8'))
    handshake_hash = sha1_hasher.hexdigest()
    S_PUB = util.get_public_key_cert(server_cert)
    handshake_server(S_PUB, R_CLIENT, K, handshake_hash)
    
    # Generate keys using the master secret.
    keys = util.generate_keys(K)

    # Listen for data from the server.
    listen_for_data(keys)


def handshake_server(S_PUB, R_CLIENT, K, handshake_hash):
    encrypted_secret = util.rsa_encrypt(bytes.fromhex(K), S_PUB).hex()
    encrypted_nonce = util.rsa_encrypt(bytes.fromhex(R_CLIENT), S_PUB).hex()
    request = { 'type' : "handshake",
                'nonce' : encrypted_nonce,
                'secret' : encrypted_secret,
                'hash' : handshake_hash }
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', SERVER_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    print()
    print("Sending server S_PUB{{R_CLIENT}}.")
    print("S_PUB{{R_CLIENT}}: {}".format(encrypted_nonce))
    
    print()
    print("Sending server encrypted secret and hash.")
    print("R_BOB{{S}}: {}".format(encrypted_secret))
    print()
    print("Client handshake hash: {}".format(handshake_hash))
    print()
    response = sock.recv(32768)
    response = json.loads(response)
    sock.close()
    print("Received server handshake hash from the server.")
    # Check the handshake hash.
    sha1_hasher = SHA1.new()
    sha1_hasher.update(("SERVER" + handshake_messages + "TRUDY").encode('utf-8'))
    handshake_hash = sha1_hasher.hexdigest()
    if handshake_hash == response['hash']:
        print("Handshake hash from server matches.")
        print("Expected: {}".format(request['hash']))
        print("Actual: {}".format(handshake_hash))
    else:
        raise Exception("Handshake hash from server mismatch.")
    print()
    print("-----------------------------------------------")
    print("HANDSHAKE COMPLETE.")
    print("-----------------------------------------------")
    return


def initial_contact(R_CLIENT, client_cert):
    global handshake_messages
    # Dump the client's certificate string.
    cert = crypto.dump_certificate(crypto.FILETYPE_PEM, client_cert).decode()
    # Generate a random number R_ALICE.
    request = { 'type' : "initial",
                'algorithm' : 'RSA',
                'message' : "I want to talk to you",
                'cert' : cert }
    # Send initial contact message to Bob.
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', SERVER_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    print()
    print("Making initial contact with the server.")
    print()
    print("Algorithm: RSA")
    print()
    print("Client SSL Certificate:\n {}".format(cert))
    response = sock.recv(32768)
    response = json.loads(response)
    sock.close()
    handshake_messages += json.dumps(request) + json.dumps(response)
    return response


def listen_for_data(keys):
    S_ENC = keys['S_ENC']
    S_INT = keys['S_INT']
    C_ENC = keys['C_ENC']
    C_INT = keys['C_INT']

    # Setup socket to listen for new connections.
    lis_sock = socket(AF_INET, SOCK_STREAM)
    lis_sock.bind(('', CLIENT_PORT))
    lis_sock.listen(1)

    seq = 1
    buffer = ""
    while 1:
        # Incoming request.
        conn_sock, addr = lis_sock.accept()
        packet = conn_sock.recv(10000000)
        request = json.loads(packet.decode('utf-8'))
        encrypted_record = request['record']
        record = util.decrypt_plaintext(S_ENC, encrypted_record)
        msg = record[0:20000]
        HMAC = record[20000:]
        expected_HMAC = util.generate_HMAC(S_INT, str(seq) + request['header'] + msg)
        print("Got SSL record {} from server.".format(seq))
        print("Header: {}".format(request['header']))
        print("Expected HMAC: {}".format(expected_HMAC))
        print("Received HMAC: {}".format(HMAC))
        print("HMAC is correct.")
        print("Decrypting message and adding to buffer.")
        print()
        if expected_HMAC != HMAC:
            raise Exception("HMAC integrity failure.")
        # Add partial message to the buffer and update the sequence
        buffer = buffer + bytes.fromhex(msg).decode('utf-8')
        seq = seq + 1
        if seq == 6:
            util.diff(buffer)
            return


if __name__ == "__main__":
    main()
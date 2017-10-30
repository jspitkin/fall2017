"""
    Jake Pitkin - u0891770
    CS 6490 - Fall 2017
    Programming Assignment 4
"""

from socket import *
from Crypto import Random
from Crypto.Hash import SHA1
from Crypto.Cipher import AES
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
    R_CLIENT = util.generate_random_number()
    print()
    print("Creating R_CLIENT.")
    print("R_CLIENT: {}".format(R_CLIENT))
    print()
    client_cert = util.read_certificate(CLIENT_CERT_PATH)

    # Message 1 - initial contact with Bob
    response = initial_contact(R_CLIENT, client_cert)

    # Extract the server's nonce.
    R_SERVER = response['nonce']
    server_cert = response['cert']
    print()
    print("Received initial response from the server.")
    print("R_SERVER: {}".format(R_SERVER))
    print()

    # Generate the master secret.
    S = Random.get_random_bytes(32).hex()
    print("Creating random S.")
    print("S: {}".format(S))
    K = util.generate_master_secret(S, R_CLIENT, R_SERVER)
    print("Creating master key from S, R_CLIENT, and R_SERVER.")
    print("K: {}".format(K))
    print()

    # Compute the hash of the handshake messages
    handshake_messages += K
    sha1_hasher = SHA1.new()
    sha1_hasher.update(("CLIENT" + handshake_messages).encode('utf-8'))
    handshake_hash = sha1_hasher.hexdigest()
    handshake_server(R_SERVER, K, handshake_hash)

    # TODO: Verify certificates
    # TODO: Generate 4 keys with K


def handshake_server(R_SERVER, K, handshake_hash):
    cipher = AES.new(bytes.fromhex(R_SERVER), AES.MODE_ECB)
    encrypted_secret = cipher.encrypt(bytes.fromhex(K))
    print("cipher: {}".format(encrypted_secret.hex()))
    request = { 'type' : "handshake",
                'secret' : encrypted_secret.hex(),
                'hash' : handshake_hash }
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', SERVER_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    print()
    print("Sending server encrypted secret and hash.")
    print("R_BOB{{S}}: {}".format(encrypted_secret))
    print("Client handshake hash: {}".format(handshake_hash))
    print()
    response = sock.recv(1024)
    response = json.loads(response)
    sock.close()
    print("Received server handshake hash from the server.")
    # Check the handshake hash.
    sha1_hasher = SHA1.new()
    sha1_hasher.update(("SERVER" + handshake_messages).encode('utf-8'))
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


def initial_contact(R_CLIENT, client_cert):
    global handshake_messages
    # Dump the client's certificate string.
    cert = crypto.dump_certificate(crypto.FILETYPE_PEM, client_cert).decode()
    # Generate a random number R_ALICE.
    request = { 'type' : "initial",
                'algorithm' : 'RSA',
                'message' : "I want to talk to you",
                'nonce' : R_CLIENT,
                'cert' : cert }
    # Send initial contact message to Bob.
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(('', SERVER_PORT))
    packet = json.dumps(request).encode('utf-8')
    sock.send(packet)
    print()
    print("Making initial contact with the server.")
    print("R_ALICE: {}".format(R_CLIENT))
    print("Algorithm: RSA")
    print()
    response = sock.recv(1024)
    response = json.loads(response)
    sock.close()
    handshake_messages += json.dumps(request) + json.dumps(response)
    return response

if __name__ == "__main__":
    main()
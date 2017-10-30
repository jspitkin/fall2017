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
SERVER_CERT_PATH = "server.crt"
SERVER_KEY_PATH = "server.key"
handshake_messages = ""


def main():
    global handshake_messages
    # Setup socket to listen for new connections.
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.bind(('', SERVER_PORT))
    serv_sock.listen(1)

    while 1:
        # Incoming request.
        conn_sock, addr = serv_sock.accept()
        packet = conn_sock.recv(32768)
        request = json.loads(packet.decode('utf-8'))
        # Determine request type.
        if request['type'] == "initial":
            R_CLIENT = request['nonce']
            handshake_messages += json.dumps(request)
            R_SERVER = send_certificate(conn_sock)            
        elif request['type'] == "handshake":
            send_handshake_hash(conn_sock, request, R_SERVER)

    # TODO: Verify certificates
    # TODO: Generate 4 keys with K


def send_certificate(conn_sock):
    global handshake_messages
    # Create a certificate and key pair for the server.
    util.create_certificate_and_key(SERVER_CERT_PATH, SERVER_KEY_PATH)

    # Generate a random number R_BOB.
    R_SERVER = util.generate_random_number()
    cert = util.read_certificate(SERVER_CERT_PATH)
    cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode()
    request = { 'type' : "initial",
                'algorithm' : "RSA",
                'nonce' : R_SERVER,
                'cert' : cert }
    handshake_messages += json.dumps(request)
    # Send R_BOB and certificate to client.
    packet = json.dumps(request).encode('utf-8')
    conn_sock.send(packet)
    print()
    print("Sending client R_BOB and certificate.")
    print("R_BOB: {}".format(R_SERVER))
    print("Algorithm: RSA")
    print()
    return R_SERVER


def send_handshake_hash(conn_sock, request, R_SERVER):
    global handshake_messages

    # Recover the master secret using the server's key.
    cipher = AES.new(bytes.fromhex(R_SERVER), AES.MODE_ECB)
    print()
    print("Decrypting master secret.")
    print("Encrypted S: {}".format(request['secret']))
    K = cipher.decrypt(bytes.fromhex(request['secret'])).hex()
    print("S: {}".format(K))
    print()
    print("Checking handshake hash.")
    handshake_messages += K

    # Check the handshake hash.
    sha1_hasher = SHA1.new()
    sha1_hasher.update(("CLIENT" + handshake_messages).encode('utf-8'))
    handshake_hash = sha1_hasher.hexdigest()
    if handshake_hash == request['hash']:
        print("Handshake hash from client matches.")
        print("Expected: {}".format(request['hash']))
        print("Actual: {}".format(handshake_hash))
    else:
        raise Exception("Handshake hash from client mismatch.")
    
    # Handshake hash matches, respond with server's handshake hash.
    sha1_hasher = SHA1.new()
    sha1_hasher.update(("SERVER" + handshake_messages).encode('utf-8'))
    server_hash = sha1_hasher.hexdigest()
    request = { 'hash' : server_hash }
    packet = json.dumps(request).encode('utf-8')
    conn_sock.send(packet)
    print()
    print("Sending client hash of handshake messages.")
    print("Server handshake hash: {}".format(server_hash))
    print()
    print("-----------------------------------------------")
    print("HANDSHAKE COMPLETE.")
    print("-----------------------------------------------")



if __name__ == "__main__":
    main()

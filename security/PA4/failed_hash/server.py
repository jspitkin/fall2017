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
            handshake_messages += json.dumps(request)
            R_SERVER = send_certificate(conn_sock, request)            
        elif request['type'] == "nonce":
            verify_client_nonce()
        elif request['type'] == "handshake":
            K = send_handshake_hash(conn_sock, request, R_SERVER)

            # Generate keys using the master secret.
            keys = util.generate_keys(K)
            send_data(keys)
            return

def send_certificate(conn_sock, request):
    global handshake_messages
    # Create a certificate and key pair for the server.
    util.create_certificate_and_key(SERVER_CERT_PATH, SERVER_KEY_PATH)
    print()
    print("Received certificate from client.")
    print()
    print("Client SSL Certificate:\n {}".format(request['cert']))

    # Generate a random number R_BOB.
    R_SERVER = Random.get_random_bytes(32).hex()
    print()
    print("Creating R_SERVER.")
    print("R_SERVER: {}".format(R_SERVER))
    print()
    client_cert = crypto.load_certificate(crypto.FILETYPE_PEM, request['cert'])
    client_pub_key = util.get_public_key_cert(client_cert)
    encrypted_nonce = util.rsa_encrypt(bytes.fromhex(R_SERVER), client_pub_key)
    cert = util.read_certificate(SERVER_CERT_PATH)
    cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode()
    request = { 'type' : "initial",
                'algorithm' : "RSA",
                'nonce' : encrypted_nonce.hex(),
                'cert' : cert }
    handshake_messages += json.dumps(request)
    # Send R_BOB and certificate to client.
    packet = json.dumps(request).encode('utf-8')
    conn_sock.send(packet)
    print()
    print("Extracting C_PUB from client's certificate.")
    print("Sending client C_PUB{{R_SERVER}} and server's certificate.")
    print("C_PUB{{R_SERVER}}: {}".format(encrypted_nonce.hex()))
    print()
    print("Algorithm: RSA")
    print()
    print("Server SSL Certificate:\n {}".format(cert))
    return R_SERVER


def send_handshake_hash(conn_sock, request, R_SERVER):
    global handshake_messages

    # Recover the master secret using the server's key.
    print()
    print("Decrypting master secret.")
    print("R_BOB{{S}}: {}".format(request['secret']))
    print()
    K = util.rsa_decrypt(bytes.fromhex(request['secret']), util.get_private_key(SERVER_KEY_PATH))
    print("K: {}".format(K.hex()))
    print()
    print("Checking handshake hash.")
    handshake_messages += K.hex()

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
    return K.hex()

def send_data(keys):
    S_ENC = keys['S_ENC']
    S_INT = keys['S_INT']
    C_ENC = keys['C_ENC']
    C_INT = keys['C_INT']
    util.generate_50kbyte_file()
    data = util.read("test.txt")

    start = 0
    end = 10000
    seq_num = 1
    # Send 10K of data at a time.
    for i in range (5):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect(('', CLIENT_PORT))
        cur_data = data[start:end]
        header, record, HMAC = util.generate_SSL_data_record(S_ENC, 
            S_INT, cur_data, seq_num)
        request = { 'header' : header,
                    'record' : record }
        packet = json.dumps(request).encode('utf-8')
        sock.send(packet)
        print("Sending SSL record number {}".format(seq_num))
        print("Header: {}".format(header))
        print("HMAC: {}".format(HMAC))
        print()
        seq_num = seq_num + 1
        start = start + 10000
        end = end + 10000
        sock.close()
    print()
    print("-----------------------------------------------")
    print("DATA TRANSFER COMPLETE.")
    print("-----------------------------------------------")
    return


if __name__ == "__main__":
    main()

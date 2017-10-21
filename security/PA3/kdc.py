from socket import *
from Crypto import Random
import json


def main():
    KDC_PORT = 12000
    kdc_registry = {}

    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.bind(('', KDC_PORT))
    serv_sock.listen(1)

    while 1:
        # listen for connections
        conn_sock, addr = serv_sock.accept()

        packet = conn_sock.recv(1024)
        request = json.loads(packet.decode('utf-8'))
        if request['type'] == "register":
            register_user(conn_sock, request['data'], kdc_registry)


def register_user(conn_sock, user_id, registry):
    """ Attempts to register a new user in the KDC. Returns -1 if the user is already registered.

    Args:
        conn_sock (socket): User's socket.
        user_id (string): User's id in hexadecimal.
        registry (dict): Registry of registered users and their keys.

    Return:
        None.
    
    """
    if user_id in registry:
        print("User already registered with the KDC.")
        success = -1
        new_key = ""
    else:
        success = 1
        new_key = Random.get_random_bytes(24).hex()
    registry[user_id] = new_key
    response = { 'type' : "register",
                 'data' : new_key,
                 'success' : success }
    packet = json.dumps(response).encode('utf-8')
    print("Sending user their private key")
    conn_sock.send(packet)


if __name__ == "__main__":
    main()
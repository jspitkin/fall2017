""" 
    Jake Pitkin - u0891770
    CS - 6490 Fall 2017
    Programming Assignment #2
"""

from socket import *
from expo import exponentiate

SERVER_PORT = 12000
SB = 12067 # Bob's secret key
g = 1907 # Public prime base
p = 784313 # Public prime modulus

serv_sock = socket(AF_INET, SOCK_STREAM)
serv_sock.bind(('', SERVER_PORT))
serv_sock.listen(1)

while 1:
    # Listen for Alice to connect to Bob
    conn_sock, addr = serv_sock.accept()

    # Compute Bob's public key
    TB = exponentiate(g, SB, p)
    print("Bob's public key on the server: {}".format(TB))

    # Listen for Alice's public key
    TA = conn_sock.recv(1024)
    print("Alice's public key on the server: {}".format(int(TA)))

    # Send Bob's public key
    conn_sock.send(str(TB).encode())

    # Compute shared key
    secret = exponentiate(int(TA), SB, p)
    print("Shared secret key on server: {}".format(secret))
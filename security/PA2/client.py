""" 
    Jake Pitkin - u0891770
    CS - 6490 Fall 2017
    Programming Assignment #2
"""

from socket import *
from expo import exponentiate

SERVER_PORT = 12000
SA = 160011 # Alice's secret key
g = 1907 # Public prime base
p = 784313 # Public prime modulus

client_sock = socket(AF_INET, SOCK_STREAM)
client_sock.connect(('', SERVER_PORT))

# Compute Alice's public key
TA = exponentiate(g, SA, p)
print("Alice's public key on the client: {}".format(TA))

# Send Alice's public key
client_sock.send(str(TA).encode())

# Receive Bob's public key
TB = client_sock.recv(1024)
print("Bob's public key on the client: {}".format(int(TB)))

# Compute shared key
secret = exponentiate(int(TB), SA, p)
print("Shared secret key on the client: {}".format(secret))
""" jsp sept 8 2017 """

from socket import *
from expo import exponentiate

SERVER_PORT = 12000
SA = 160011
g = 1907
p = 784313

client_sock = socket(AF_INET, SOCK_STREAM)
client_sock.connect(('', SERVER_PORT))

TA = exponentiate(g, SA, p)
print("TA on the client: {}".format(TA))
client_sock.send(str(TA).encode())
TB = client_sock.recv(1024)
print("TB on the client: {}".format(int(TB)))
secret = exponentiate(int(TB), SA, p)
print("Shared secret key on the client: {}".format(secret))
""" jsp sept 8 2017 """

from socket import *
from expo import exponentiate

SERVER_PORT = 12000
SB = 12067
g = 1907
p = 784313

serv_sock = socket(AF_INET, SOCK_STREAM)
serv_sock.bind(('', SERVER_PORT))
serv_sock.listen(1)

while 1:
    conn_sock, addr = serv_sock.accept()
    TB = exponentiate(g, SB, p)
    print("TB on the server: {}".format(TB))
    TA = conn_sock.recv(1024)
    print("TA on the server: {}".format(int(TA)))
    conn_sock.send(str(TB).encode())
    secret = exponentiate(int(TA), SB, p)
    print("Shared secret key on server: {}".format(secret))
from socket import *

SERVER_NAME = ''
SERVER_PORT = 12000

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((SERVER_NAME, SERVER_PORT))

sentence = input('Input lowercase sentence:')
client_socket.send(sentence.encode())
modified_sentence = client_socket.recv(1024)

print('From Server: ', str(modified_sentence)
client_socket.close()
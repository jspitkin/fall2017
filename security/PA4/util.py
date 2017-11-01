"""
    Jake Pitkin - u0891770
    CS 6490 - Fall 2017
    Programming Assignment 4
"""

import time
import math
import sys
import os.path
import random as r
from Crypto import Random
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from OpenSSL import crypto
from Crypto.Hash import SHA256
from Crypto.Hash import HMAC
from Crypto.Cipher import DES3
from Crypto.Util import Padding


def generate_master_secret(n1, n2):
    """ Generates a 32-byte master secret by performing an xor
        function on the client and server's nonces.abs

        Args:
            n1 (string) - client's nonce in hexadecimal.
            n2 (string) - server's nonce in hexadecimal.
        
        Return:
            master_secret (hex) - xor'ed shared secret.
    """
    n1_bytes = bytes.fromhex(n1)
    n2_bytes = bytes.fromhex(n2)
    xor_bytes = []
    for b1, b2 in zip(n1_bytes, n2_bytes):
        xor_bytes.append(bytes([b1 ^ b2]))
    return (b''.join(xor_bytes)).hex()


def create_certificate_and_key(cert_path, key_path):
    print()
    print("Creating SSL certificate and key set.")
    # If the certificate and key pair already exist, do nothing.
    if os.path.isfile(cert_path) and os.path.isfile(key_path):
        return

    # Generate the key pair.
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 1024)

    # Generate the certificate.
    certificate = crypto.X509()
    certificate.get_subject().C = "US"
    certificate.get_subject().ST = "Utah"
    certificate.get_subject().L = "Salt Lake City"
    certificate.get_subject().O = "jsp"
    certificate.get_subject().OU = "University of Utah"
    certificate.get_subject().CN = "localhost"
    certificate.gmtime_adj_notBefore(0)
    certificate.gmtime_adj_notAfter(int(math.pow(2, 32)))
    certificate.set_serial_number(10)
    certificate.set_issuer(certificate.get_subject())
    certificate.set_pubkey(key)
    certificate.sign(key, 'sha1')

    # Write the key pair to file.
    with open(key_path, 'wb') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    
    # Write the certificate to file.
    with open(cert_path, 'wb') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, certificate))
    return


def read_certificate(cert_path):
    with open(cert_path, 'r') as f:
        cert = f.read()
    certificate = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    return certificate


def read_key(key_path):
    with open(key_path, 'r') as f:
        k = f.read()
    key = crypto.load_privatekey(crypto.FILETYPE_PEM, k)
    return key


def get_public_key(key_path):
    keys = read_key(key_path)
    public_key = crypto.dump_publickey(crypto.FILETYPE_PEM, keys)
    key_bytes = crypto.load_publickey(crypto.FILETYPE_PEM, public_key)
    rsa_public_key = key_bytes.to_cryptography_key()
    return rsa_public_key


def get_private_key(key_path):
    keys = read_key(key_path)
    private_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, keys)
    key_bytes = crypto.load_privatekey(crypto.FILETYPE_PEM, private_key)
    rsa_private_key = key_bytes.to_cryptography_key()
    return rsa_private_key


def get_public_key_cert(cert):
    public_key = cert.get_pubkey()
    pub_key = crypto.dump_publickey(crypto.FILETYPE_PEM, public_key)
    key_bytes = crypto.load_publickey(crypto.FILETYPE_PEM, pub_key)
    rsa_public_key = key_bytes.to_cryptography_key()
    return rsa_public_key


def get_padding():
    return padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA1()), algorithm=hashes.SHA1(), label=None)


def rsa_encrypt(plaintext, public_key):
    return public_key.encrypt(plaintext, get_padding())


def rsa_decrypt(ciphertext, private_key):
    return private_key.decrypt(ciphertext, get_padding())


def generate_50kbyte_file():
    """ Generate a file containing 50,000 bytes. """
    characters = ["a", "b", "c", "x", "y", "z", " "]
    output_string = ""
    for i in range(1000):
        for j in range(49):
            output_string += r.choice(characters)
        output_string += '\n'
    with open('test.txt', 'w') as f:
        f.write(output_string)


def generate_keys(K):
    print()
    print("Generating keys from master secret.")
    serv_encrypt = K[0:32]
    serv_integ = K[32:]
    sha256_hasher = SHA256.new()
    sha256_hasher.update(bytes.fromhex(K))
    K = sha256_hasher.hexdigest()
    client_encrypt = K[0:32]
    client_integ = K[32:]
    print("S_ENC: {}".format(serv_encrypt))
    print("S_INT: {}".format(serv_integ))
    print("C_ENC: {}".format(client_encrypt))
    print("C_INT: {}".format(client_integ))
    print()
    keys = { 'S_ENC' : serv_encrypt,
             'S_INT' : serv_integ,
             'C_ENC' : client_encrypt,
             'C_INT' : client_integ }
    return keys


def generate_HMAC(key, message):
    message = message.encode('utf-8')
    h = HMAC.new(bytes.fromhex(key), digestmod=SHA256)
    h.update(message)
    return h.hexdigest()


def encrypt_plaintext(key, plaintext):
    """ Encrypts plaintext with the given key.

        Args:
            key (hex): DES3 key.
            plaintext (hex): unpadded plaintext.

        Return:
            ciphertext (hex): padded encrypted plaintext.
    """

    key = bytes.fromhex(key)
    plaintext = bytes.fromhex(plaintext)
    des3 = DES3.new(key, DES3.MODE_ECB)
    ciphertext = des3.encrypt(Padding.pad(plaintext, DES3.block_size))
    return ciphertext.hex()


def decrypt_plaintext(key, ciphertext):
    """ Decrypts a ciphertext with the given key.
        
        Args:
            key (hex): DES3 key.
            ciphertext (hex): padded ciphertext.
        
        Return:
            unpadded_plaintext (hex): decrypted plaintext.
    """

    key = bytes.fromhex(key)
    ciphertext = bytes.fromhex(ciphertext)
    des3 = DES3.new(key, DES3.MODE_ECB)
    plaintext = des3.decrypt(ciphertext)
    unpadded_plaintext = Padding.unpad(plaintext, DES3.block_size)
    return unpadded_plaintext.hex()


def generate_SSL_data_record(enc_key, int_key, msg, seq):
    record = ""
    header = "application_data "
    header += "23 "
    header += "10k"
    msg = msg.encode('utf-8').hex()
    HMAC = generate_HMAC(int_key, str(seq) + header + msg)
    cipher = encrypt_plaintext(enc_key, msg + HMAC)
    return header, cipher, HMAC


def diff(data):
    expected_data = read('test.txt')
    if expected_data != data:
        raise Exception("Diff of received data fails with original file.")
    print()
    print("-----------------------------------------------")
    print("DATA TRANSFER COMPLETE.")
    print("-----------------------------------------------")
    print()
    print("Full message received from server.")
    print("Performing diff on message . . . ")
    print()
    print("Diff of file is correct.")


def read(path):
    result = ""
    with open(path, 'r') as f:
        for line in f:
            result += line
    return result
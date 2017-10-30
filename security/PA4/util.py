"""
    Jake Pitkin - u0891770
    CS 6490 - Fall 2017
    Programming Assignment 4
"""

import time
import math
import sys
import os.path
from Crypto import Random
from OpenSSL import crypto


def generate_random_number():
    """ Generates a 32-byte random number where
        the first four bytes are the Unix time.

        Return:
            nonce (string) - hexadecimal format.
    """
    unix_time = (math.floor(time.time())).to_bytes(32, byteorder='big')
    unix_time_four_bytes = unix_time[28:]
    nonce = Random.get_random_bytes(28)
    nonce = unix_time_four_bytes + nonce
    return nonce.hex()


def generate_master_secret(S, n1, n2):
    """ Generates a 32-byte master secret by performing an xor
        function on the client and server's nonces.abs

        Args:
            S (string) - pre-master secret in hexadecimal.
            n1 (string) - client's nonce in hexadecimal.
            n2 (string) - server's nonce in hexadecimal.
        
        Return:
            master_secret (hex) - xor'ed shared secret.
    """
    S_bytes = bytes.fromhex(S)
    n1_bytes = bytes.fromhex(n1)
    n2_bytes = bytes.fromhex(n2)
    xor_bytes = []
    for b1, b2 in zip(n1_bytes, n2_bytes):
        xor_bytes.append(bytes([b1 ^ b2]))
    xor_bytes = b''.join(xor_bytes)
    master_secret = []
    for S_byte, xor_byte in zip(S_bytes, xor_bytes):
        master_secret.append(bytes([S_byte ^ xor_byte]))
    return (b''.join(master_secret)).hex()


def create_certificate_and_key(cert_path, key_path):
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

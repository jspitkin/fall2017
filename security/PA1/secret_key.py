""" CS-6490 Network Security -- Fall 2017
    Programming Assignment 1
    Jake Pitkin -- u0891770 -- jakepitkin@gmail.com 
    Secret key encryption and decryption """
import sys
import array
import random


ROUNDS = 16
MSG_LENGTH = 8
KEY = None
ENCRYPT_SUB_TABLES = []
DECRYPT_SUB_TABLES = []
LOG = []


def main():
    """ program entry point. """
    global KEY

    if invalid_input(sys.argv):
        return -1

    message = array.array('B', sys.argv[1].encode())
    KEY = array.array('B', sys.argv[2].encode())

    # encryption phase
    create_substitution_table_encrypt()
    cipher_text = encrypt(message)

    # decryption phase
    create_substitution_table_decrypt()
    decrypted_message = decrypt(cipher_text)

    write_log()


def encrypt(msg):
    LOG.append("Encryption Begins")
    LOG.append("Initial Message:\t\t" + str(byte_to_char(msg))
                + "\t\t" + byte_array_to_hex(msg))
    LOG.append("")
    for r in range(ROUNDS):
        # xor the message and the key
        msg = xor_byte_arrays(msg, KEY)
        # character-by-character substitution with the encrypt table
        for msg_index in range(MSG_LENGTH):
            msg[msg_index] = ENCRYPT_SUB_TABLES[msg_index][msg[msg_index]]
        # permute the bits left
        bit_string = ""
        for msg_index in range(MSG_LENGTH):
            bit_string += byte_to_binary(msg[msg_index])
        bit_string = bit_string[1:] + bit_string[0]
        # convert bits back to bytes
        msg = array.array('B', [])
        for _ in range(MSG_LENGTH):
            msg.append(int(bit_string[0:8], 2))
            bit_string = bit_string[8:]
        LOG.append("Encryption Round " + str(r + 1) + ": \t" + str(byte_to_char(msg))
                    + "\t\t" + byte_array_to_hex(msg))
    LOG.append("")
    return msg


def decrypt(msg):
    LOG.append("Decryption Begins")
    LOG.append("Cipher Text:\t\t\t" + str(byte_to_char(msg))
                + "\t\t" + byte_array_to_hex(msg))
    LOG.append("")
    for r in range(ROUNDS):
        # permute the bits right
        bit_string = ""
        for msg_index in range(MSG_LENGTH):
            bit_string += byte_to_binary(msg[msg_index])            
        bit_string = bit_string[-1] + bit_string[:-1]
        # convert bits back to bytes
        msg = array.array('B', [])
        for _ in range(MSG_LENGTH):
            msg.append(int(bit_string[0:8], 2))
            bit_string = bit_string[8:]
        # character-by-character substitution with the decrypt table
        for msg_index in range(MSG_LENGTH):
            msg[msg_index] = DECRYPT_SUB_TABLES[msg_index][msg[msg_index]]
        # xor the message and the key
        msg = xor_byte_arrays(msg, KEY)
        LOG.append("Decryption Round " + str(r + 1) + ": \t" + str(byte_to_char(msg))
                    + "\t\t" + byte_array_to_hex(msg))
    LOG.append("")
    LOG.append("Recovered Message:\t" + str(byte_to_char(msg)) + "\t\t" 
                    + byte_array_to_hex(msg))
    return msg


def create_substitution_table_encrypt():
    # Create 8 tables that each map [0, 255] to a random value [0, 255]
    for table_index in range(MSG_LENGTH):
        random_chars = [i for i in range(256)]
        random.seed(get_seed())
        random.shuffle(random_chars)
        ENCRYPT_SUB_TABLES.append(random_chars)


def create_substitution_table_decrypt():
    # create a copy of the encrypt table and invert
    tmp_table = []
    for table_index in range(MSG_LENGTH):
        random_chars = [i for i in range(256)]
        random.seed(get_seed())
        random.shuffle(random_chars)
        tmp_table.append(random_chars)
    # Invert table for decrypting
    for table_index in range(MSG_LENGTH):
        inverted_table = [0 for _ in range(256)]
        for encrypt_table_index in range(256):
            inverted_table[tmp_table[table_index][encrypt_table_index]] = encrypt_table_index
        DECRYPT_SUB_TABLES.append(inverted_table) 


def invalid_input(args):
    if len(args) != 3:
        print("useage: python3 secret_key.py <message> <key>")
        return True
    if len(args[1]) != MSG_LENGTH:
        print("message must be 8 characters")
        return True
    if len(args[2]) != MSG_LENGTH:
        print("key must be 8 characters")
        return True
    return False


def xor_byte_arrays(a1, a2):
    """ a1 and a2 must be of length 8 """
    result = array.array('B', [0 for i in range(MSG_LENGTH)])
    for i in range(MSG_LENGTH):
        result[i] = a1[i] ^ a2[i]
    return result


def byte_to_binary(byte):
    return "{0:08b}".format(byte)


def byte_array_to_string(bytes):
    return "".join(map(chr, bytes))


def byte_array_to_hex(bytes):
    hex_string = ""
    for b in bytes:
        hex_string = hex_string + format(b, 'x') + " "
    return hex_string.strip()


def byte_to_char(bytes):
    chars = [chr(b) for b in bytes]
    return chars        


def write_log():
    file = open("test.trace", 'w')
    for i in range(len(LOG)):
        file.write(LOG[i] + "\n")


def get_seed():
    return byte_array_to_string(KEY)


if __name__ == '__main__':
    main()
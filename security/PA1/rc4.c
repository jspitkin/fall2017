/*  CS-6490 Network Security -- Fall 2017
    Programming Assignment 1
    Jake Pitkin -- u0891770 -- jakepitkin@gmail.com
    RC4 implementation based off text by Kaufman, Perlman and Speciner */
#include <stdio.h>

typedef unsigned char uns8;
typedef unsigned short uns16;

/* 258 octets of state information */
static uns8 state[256];
static uns8 x;
static uns8 y;

void rc4init(uns8 *key, uns16 length);
uns8 rc4step();

int main() {
    int msg_len = 30;
    int skip_count = 512;
    uns8 key[] = "mnbvc";
    uns8 msg[] = "This class is not hard at all.";
    uns8 cipher[msg_len];
    uns8 decrypted_msg[msg_len];

    // initialize
    printf("Key: %s\n", key);
    printf("Original message: %s\n", msg);
    rc4init(key, 5);

    // ignore the first 512 generated octets
    for (int i = 0; i < skip_count; i++) {
        rc4step();
    }

    // encrypt message
    printf("Cipher text: ");
    for (int i = 0; i < msg_len; i++) {
        cipher[i] = msg[i] ^ rc4step();
        printf("%u", cipher[i]);
    }
    printf("\n");

    // initialize
    rc4init(key, 5);

    // ignore the first 512 generated octets
    for (int i = 0; i < skip_count; i++) {
        rc4step();
    }

    // decrypt message
    printf("Decrypted message: ");
    for (int i = 0; i < 30; i++) {
        decrypted_msg[i] = cipher[i] ^ rc4step();
        printf("%c", decrypted_msg[i]);
    }
    printf("\n");

}

void rc4init(uns8 *key, uns16 length) {   /* initialize for encryption / decrytion */
    int i;
    uns8 t;
    uns8 j;
    uns8 k = 0;

    for (i = 256; i--; ) {
        state[i] = i;
    }

    for (i = 0, j = 0; i < 256; i++, j = (j + i) % length) {
        t = state[i];
        state[i] = state[k += key[j] + t];
        state[k] = t;
    }

    x = 0;
    y = 0;
}

uns8 rc4step() {    /* return next pseudo-random octet */
    uns8 t;

    t = state[y += state[++x]];
    state[y] = state[x];
    state[x] = t;

    // Code fix: mod the index by the state size
    return (state[(state[x] + state[y]) % 256]);
}
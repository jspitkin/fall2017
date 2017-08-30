/*  CS-6490 Network Security -- Fall 2017
    Programming Assignment 1
    Jake Pitkin -- u0891770 -- jakepitkin@gmail.com
    RC4 implementation based off text by Kaufman, Perlman and Speciner */

typedef unsigned char uns8;
typedef unsigned short uns16;

/* 258 octets of state information */
static uns8 state[256];
static uns8 x;
static uns8 y;

void rc4init(uns8 *key, uns16 length);
uns8 rec4step();

int main() {
    //string msg = "This class is not hard at all.";
    uns8 key = "mnbvc";
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

    return (state[state[x] + state[y]]);
}
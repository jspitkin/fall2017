CS-6490 Network Security -- Fall 2017
Programming Assignment 1
Jake Pitkin -- u0891770 -- jakepitkin@gmail.com

Part 1: RC4

My program is written in c and was tested on CADE machine lab1-18.

---
Cipher text for "This class is not hard at all."
---
17338121873991361802471671122516235133236106112157122921981091961645222524175195

---
How to use
---
The command to run my program on the CADE machine is: "gcc rc4.c && ./a.out"
This will compile and execute the encryption and decryption process.

----------------------------------------------------------------------------------------

Part 2: Secret key encryption and decryption

My program is written in Python3 and was tested on CADE machine lab1-18.
I have generated sample output of my program for the messages 'kerplunk' and
'kerplunj'. This output can be found in kerplunk.trace and kerplunj.trace respectively.
The trace files contain the round, the array of characters, and their hex value on each row.

I used the key 'wizardly' when testing.

The key is used to seed the creation of the substitution tables,
so encryption and decryption could work across two separate machines/programs. 
I coupled encryption and decryption into one program to make grading easier.

---
How to use
---
The command to run the program is "python3 secret_key.py <message> <key>".
For example to run my program with the word 'kerplunk' and key 'wizardly' you would
use 'python3 secret_key.py kerplunk wizardly'.

Running my program currently will write the output to 'test.trace'.

Thank you
CS-6490 Network Security -- Fall 2017
Programming Assignment 1
Jake Pitkin -- u0891770 -- jakepitkin@gmail.com


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
The command to run program is "python3 secret_key.py <message> <key>".
For example to run my program with the word 'kerplunk' and key 'wizardly' you would
use 'python3 secret_key.py kerplunk wizardly'.

Running my program currently will write the output to 'test.trace'

Thank you.
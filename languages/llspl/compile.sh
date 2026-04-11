#!/bin/bash
python main.py "$1" > program.asm
nasm -f elf64 program.asm -o program.o
ld program.o -o program
rm program.o program.asm

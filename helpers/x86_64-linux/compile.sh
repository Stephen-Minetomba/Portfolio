#!/bin/bash
echo "[.] Linking..."
cat lib.asm > target.asm # statically link
echo "[✔] lib.asm linked!"
echo "[.] Adding newline..."
printf "\n" >> target.asm
echo "[✔] Newline added!"
echo "[.] Linking..."
cat main.asm >> target.asm
echo "[✔] main.asm linked!"
echo "[.] Assembling..."
nasm -f elf64 target.asm -o target.o # assemble
echo "[✔] Assembled!"
echo "[.] Linking..."
ld target.o -o main # link
echo "[✔] Linked!"
echo "[.] Cleaning up..."
rm target.o target.asm # remove artifacts
echo "[✔] Workspace clean!"
echo "🚀 Run the file by doing the command './main'."
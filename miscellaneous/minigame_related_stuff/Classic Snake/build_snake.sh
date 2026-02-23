#!/bin/bash

outputFile="snake.bin"
inputFile="snake.c"
echo "[✔] Configuration succesfully created:"
echo "| - outputFile: $outputFile"
echo "| - inputFile: $inputFile"

if [ -e "$outputFile" ]; then
    echo "[X] $outputFile exists. Removing..."
    rm $outputFile
    echo "[✔] Removed $outputFile."
fi
gcc "$inputFile"
echo "[✔] Compiled $inputFile, outputted into a.out"
mv a.out "$outputFile"
echo "[✔] Renamed a.out to $outputFile"
## About me
My name is **Stephen**, I was born in **Bucharest**, and I learned **Python**, **Rust**, **Go** and **C** when I was **14 years old**.

## About this repository
This repository will contain most of my coding projects, free and open source (still, don't copy them and use them like you were the one who created them).

## About the tools in it
### helpers/library.go
This is a **library** I made in **Go** to assist people in moving from Python to Go.
### bootloader
To compile it, let's run the compilation script.
```
chmod +x compile.sh # if not already executable
./compile.sh # will install nightly, other dependencies, and compile it
```
The EFI file should now be in **target/x86_64-unknown-uefi/release/uefi_bootloader.efi**.
Now, use QEMU to run the EFI file. Also, if you want to modify it, I built a lot of useful macros that you can use to modify the functionality.
### The solidity analyzer
The name says it all. It analyzes solidity contracts for vulnerabilities, and also allows you to analyze individual functions interactively.
### languages/
A set of all the languages/potential CPU architectures I invented.

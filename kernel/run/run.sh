#!/bin/bash
sudo qemu-system-x86_64 \
    -nodefaults \
    -nographic \
    -serial stdio \
    -drive if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd \
    -drive if=pflash,format=raw,file=OVMF_VARS.fd \
    -drive format=raw,file=fat:rw:. \
    -net none

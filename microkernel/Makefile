ASM = nasm
ASMFLAGS = -f win64

CC = x86_64-w64-mingw32-gcc
EFI_INCLUDE = /usr/include/efi
EFI_X64_INCLUDE = /usr/include/efi/x86_64
CFLAGS = -c -O2 -ffreestanding -fno-stack-protector -m64 -I$EFI_INCLUDE -I$EFI_X64_INCLUDE -fno-stack-protector -fpic -fshort-wchar

LD = lld-link
LDFLAGS = /subsystem:efi_application /entry:efi_main /machine:x64 /nodefaultlib /out:BOOTX64.EFI

ASM_SRC = main.asm
C_SRC = main.c
OBJ = main.obj main_c.obj
OUT = BOOTX64.EFI

all: $(OUT)

# Link both assembly and C objects into BOOTX64.EFI
$(OUT): $(OBJ)
	$(LD) $(LDFLAGS) $(OBJ)

# Assemble NASM file
main.obj: $(ASM_SRC)
	$(ASM) $(ASMFLAGS) $(ASM_SRC) -o main.obj

# Compile C file to COFF object
main_c.obj: $(C_SRC)
	$(CC) $(CFLAGS) $(C_SRC) -o main_c.obj

clean:
	rm -f $(OBJ) $(OUT)

.PHONY: all clean

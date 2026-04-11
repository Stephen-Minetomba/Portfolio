; ---------- SET (immediate) ----------
%macro seti8 2
    mov byte [%1], %2
%endmacro

%macro seti16 2
    mov word [%1], %2
%endmacro

%macro seti32 2
    mov dword [%1], %2
%endmacro

%macro seti64 2
    mov qword [%1], %2
%endmacro

; ---------- SET (register to memory) ----------
%macro setr8 2
    mov al, [%2]
    mov byte [%1], al
%endmacro

%macro setr16 2
    mov ax, [%2]
    mov word [%1], ax
%endmacro

%macro setr32 2
    mov eax, [%2]
    mov dword [%1], eax
%endmacro

%macro setr64 2
    mov rax, [%2]
    mov qword [%1], rax
%endmacro

; ---------- INT DECLARATIONS (global btw) ----------
%macro int8 1
    section .data
    %1 db 0
    section .text
%endmacro

%macro int16 1
    section .data
    %1 dw 0
    section .text
%endmacro

%macro int32 1
    section .data
    %1 dd 0
    section .text
%endmacro

%macro int64 1
    section .data
    %1 dq 0
    section .text
%endmacro

; ---------- ARRAY DECLARATIONS (global btw) ----------
%macro intArray8 2
    section .data
    %1 times %2 db 0
    section .text
%endmacro

%macro intArray16 2
    section .data
    %1 times %2 dw 0
    section .text
%endmacro

%macro intArray32 2
    section .data
    %1 times %2 dd 0
    section .text
%endmacro

%macro intArray64 2
    section .data
    %1 times %2 dq 0
    section .text
%endmacro

; ---------- ARRAY ACCESS (read, register index) ----------
%macro getIndexR 4 ; dest, array, index_reg, bits
    mov rax, [%2]
    mov rbx, [%3]

    ; auto compute scaling: bits / 8
    %assign SCALE %4 / 8
    imul rbx, SCALE
    add rax, rbx

    %ifidn %4, 8
        mov bl, [rax]
        mov [%1], bl
    %elifidn %4, 16
        mov bx, [rax]
        mov [%1], bx
    %elifidn %4, 32
        mov ebx, [rax]
        mov [%1], ebx
    %elifidn %4, 64
        mov rbx, [rax]
        mov [%1], rbx
    %else
        %error "Invalid bit width for getIndexR (must be 8,16,32,64)"
    %endif
%endmacro

; ---------- ARRAY ACCESS (read, immediate index) ----------
%macro getIndexI 4 ; dest, array, index_imm, bits
    mov rax, [%2]
    
    ; auto compute scaling: bits / 8
    %assign SCALE %4 / 8
    add rax, %3 * SCALE

    %ifidn %4, 8
        mov bl, [rax]
        mov [%1], bl
    %elifidn %4, 16
        mov bx, [rax]
        mov [%1], bx
    %elifidn %4, 32
        mov ebx, [rax]
        mov [%1], ebx
    %elifidn %4, 64
        mov rbx, [rax]
        mov [%1], rbx
    %else
        %error "Invalid bit width for getIndexI (must be 8,16,32,64)"
    %endif
%endmacro

; ---------- ARRAY ACCESS (write, register index) ----------
%macro setAtIndexR 4 ; array, index_reg, value, bits
    mov rax, [%1]
    mov rbx, [%2]
    
    ; auto compute scaling: bits / 8
    %assign SCALE %4 / 8
    imul rbx, SCALE
    add rax, rbx
    
    %ifidn %4, 8
        mov dl, [%3]
        mov byte [rax], dl
    %elifidn %4, 16
        mov dx, [%3]
        mov word [rax], dx
    %elifidn %4, 32
        mov edx, [%3]
        mov dword [rax], edx
    %elifidn %4, 64
        mov rdx, [%3]
        mov qword [rax], rdx
    %else
        %error "Invalid bit width for setAtIndexR (must be 8,16,32,64)"
    %endif
%endmacro

; ---------- ARRAY ACCESS (write, immediate index) ----------
%macro setAtIndexI 4 ; array, index_imm, value, bits
    mov rax, %1
    
    ; auto compute scaling: bits / 8
    %assign SCALE %4 / 8
    add rax, %2 * SCALE

    %ifidn %4, 8
        mov dl, %3
        mov byte [rax], dl
    %elifidn %4, 16
        mov dx, %3
        mov word [rax], dx
    %elifidn %4, 32
        mov edx, %3
        mov dword [rax], edx
    %elifidn %4, 64
        mov rdx, %3
        mov qword [rax], rdx
    %else
        %error "Invalid bit width for setAtIndexI (must be 8,16,32,64)"
    %endif
%endmacro

section .data
    newline_char db 10

; ---------- FUNCTION DEFINITIONS ----------
%macro func 1
section .text
global %1
%1:
%endmacro

; ---------- I/O PORT ACCESS ----------
%macro outx 3
    %ifidn %3, 8
        mov al, %2
        out %1, al
    %elifidn %3, 16
        mov ax, %2
        out %1, ax
    %elifidn %3, 32
        mov eax, %2
        out %1, eax
    %else
        %error "Invalid bit width for outx (must be 8,16,32)"
    %endif
%endmacro

%macro inx 3
    %ifidn %3, 8
        in al, %2
        mov [%1], al
    %elifidn %3, 16
        in ax, %2
        mov [%1], ax
    %elifidn %3, 32
        in eax, %2
        mov [%1], eax
    %else
        %error "Invalid bit width for inx (must be 8,16,32)"
    %endif
%endmacro

; ---------- BIT MANIPULATION ----------

; Set a bit
%macro setBit 2 ; reg, bit
    bts %1, %2
%endmacro

; Clear a bit
%macro clearBit 2 ; reg, bit
    btr %1, %2
%endmacro

; Test a bit
%macro testBit 2 ; reg, bit
    bt %1, %2
%endmacro

; ---------- STACK UTILITIES ----------
%macro pushRegs 0
    push rax
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
    push rbp
    push r8
    push r9
    push r10
    push r11
    push r12
    push r13
    push r14
    push r15
%endmacro

%macro popRegs 0
    pop r15
    pop r14
    pop r13
    pop r12
    pop r11
    pop r10
    pop r9
    pop r8
    pop rbp
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    pop rax
%endmacro

; ---------- KERNEL DEVELOPMENT HELPER FUNCTIONS ----------
%macro EXIT_BOOT_SERVICES 0
    push rbx
    push rbp
    mov rbp, rsp
    sub rsp, 128
    mov [rbp - 40], rdi
    mov [rbp - 48], rsi
.exit_bservices_retry:
    mov rsi, [rbp - 48]
    mov rbx, [rsi + 96]
    mov qword [rbp - 8], 0
    lea rcx, [rbp - 8]
    xor rdx, rdx
    lea r8, [rbp - 16]
    lea r9, [rbp - 24]
    lea rax, [rbp - 32]
    mov [rsp + 32], rax
    mov rax, [rbx + 56]
    call rax
    mov rcx, [rbp - 40]
    mov rdx, [rbp - 16]
    mov rax, [rbx + 232]
    call rax
    test rax, rax
    jnz .exit_bservices_retry
    mov rsp, rbp
    pop rbp
    pop rbx
%endmacro

%macro efi_setup 0
section .bss align=16
    kernel_stack: resb 4096
section .text align=16
    global efi_main
efi_main:
    sub rsp, 40
    mov rdi, rcx
    mov rsi, rdx
    EXIT_BOOT_SERVICES
    mov rsp, kernel_stack + 4096
%endmacro
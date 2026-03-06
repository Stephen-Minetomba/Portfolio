; ---------- EXIT ----------
%macro exit 1
    mov rax, 60
    mov rdi, %1
    syscall
%endmacro

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

; ---------- VARIABLE DECLARATIONS ----------
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

; ---------- ARRAYS ----------
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
    %endif
%endmacro

; ---------- SYSCALL WRAPPER ----------
%macro scall 4 ; syscall_number, fd, buffer, length
    mov rax, %1 ; first argument (syscall number)
    mov rdi, %2 ; second argument (fd)
    mov rsi, %3 ; third argument (buffer pointer)
    mov rdx, %4 ; fourth argument (length/count)
    syscall
%endmacro

; ---------- PRINT (surprisingly, this one is more useful than printstr because you have fewer rules and you also don't need to null-terminate) ----------
%macro print 2 ; address, length
    mov rax, 1
    mov rdi, 1
    mov rsi, %1
    mov rdx, %2
    syscall
%endmacro

; ---------- PRINT (auto length, very useful) ----------
%macro printstr 1 ; string label or intArray (must be null-terminated, but who am I to tell you what to do in the lowest-level human-readable programming language? do whatever you want :D)
    push rax
    push rdi
    push rsi
    push rdx
    push rcx
    
    mov rsi, %1
    xor rcx, rcx
%%count:
    cmp byte [rsi + rcx], 0
    je %%print
    inc rcx
    jmp %%count
%%print:
    mov rax, 1
    mov rdi, 1
    mov rdx, rcx
    syscall
    
    pop rcx
    pop rdx
    pop rsi
    pop rdi
    pop rax
%endmacro

; ---------- HELPER ----------
%macro newline 0
    push rax
    push rdi
    push rsi
    push rdx
    mov rax, 1
    mov rdi, 1
    mov rsi, newline_char
    mov rdx, 1
    syscall
    pop rdx
    pop rsi
    pop rdi
    pop rax
%endmacro

section .data
    newline_char db 10

%macro func 1
global %1
%1:
%endmacro
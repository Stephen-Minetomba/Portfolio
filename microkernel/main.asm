BITS 64

extern kernel
extern schedule
extern init_tasks
extern init_syscalls
extern syscall_dispatch

global efi_main
global syscall_entry
global isr_timer
global init_gdt
global init_idt
global init_paging
global switch_to_user_task
global kernel_pml4

; ================================
; CONSTANTS
; ================================

%define P_PRESENT 1
%define P_RW      2
%define P_USER    4
%define P_HUGE    0x80

; ================================
; STACK
; ================================

section .bss align=16
kernel_stack:
    resb 4096

; ================================
; PAGE TABLES
; ================================

section .bss align=4096

PML4: resq 512
PDPT: resq 512
PD:   resq 512

kernel_pml4:
    dq PML4

; ================================
; IDT
; ================================

section .data

align 16
idt_table:
    times 256 dq 0,0

idt_ptr:
    dw 256*16-1
    dq idt_table

; ================================
; GDT
; ================================

section .data

gdt_start:
    dq 0
    dq 0x00AF9A000000FFFF ; kernel code
    dq 0x00AF92000000FFFF ; kernel data
    dq 0x00AFFA000000FFFF ; user code
    dq 0x00AFF2000000FFFF ; user data
gdt_end:

gdt_ptr:
    dw gdt_end - gdt_start - 1
    dq gdt_start

; ================================
; REGISTER SAVE
; ================================

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

; ================================
; EFI ENTRY
; ================================

section .text

efi_main:

    ; rcx = image_handle
    ; rdx = system_table

    cli

    mov rsp, kernel_stack + 4096

    call init_gdt
    call init_idt
    call init_paging

    sti

    call init_tasks
    call init_syscalls

    call kernel

.halt:
    hlt
    jmp .halt

; ================================
; GDT INIT
; ================================

init_gdt:
    lgdt [gdt_ptr]
    ret

; ================================
; IDT INIT
; ================================

%macro IDT_ENTRY 2

    mov rdx, %1
    shl rdx, 4

    mov rax, %2

    mov word [idt_table + rdx + 0], ax
    mov word [idt_table + rdx + 2], 0x08
    mov byte [idt_table + rdx + 4], 0
    mov byte [idt_table + rdx + 5], 0x8E

    mov rbx, rax
    shr rbx, 16
    mov word [idt_table + rdx + 6], bx

    mov rcx, rax
    shr rcx, 32
    mov dword [idt_table + rdx + 8], ecx

    mov dword [idt_table + rdx + 12], 0

%endmacro

init_idt:

    mov rcx,0

.fill:

    cmp rcx,256
    je .done

    IDT_ENTRY rcx,isr_default

    inc rcx
    jmp .fill

.done:

    IDT_ENTRY 32,isr_timer

    lidt [idt_ptr]

    ret

isr_default:
    cli
    hlt
    iretq

; ================================
; TIMER INTERRUPT
; ================================

isr_timer:

    pushRegs

    call schedule

    popRegs

    mov al,0x20
    out 0x20,al

    iretq

; ================================
; PAGING
; ================================

init_paging:

    ; PML4 -> PDPT
    mov rax,PDPT
    or rax,P_PRESENT | P_RW
    mov [PML4],rax

    ; PDPT -> PD
    mov rax,PD
    or rax,P_PRESENT | P_RW
    mov [PDPT],rax

    ; identity map first 1GB using 2MB pages

    mov rcx,0

.map:

    cmp rcx,512
    je .done

    mov rax,rcx
    imul rax,0x200000

    or rax,P_PRESENT | P_RW | P_HUGE

    mov [PD + rcx*8],rax

    inc rcx
    jmp .map

.done:

    ; load PML4

    mov rax,PML4
    mov cr3,rax

    ; enable PAE

    mov rax,cr4
    or rax,0x20
    mov cr4,rax

    ; enable long mode

    mov ecx,0xC0000080
    rdmsr
    or eax,0x100
    wrmsr

    ; enable paging

    mov rax,cr0
    or rax,0x80000000
    mov cr0,rax

    ret

; ================================
; PHYSICAL PAGE ALLOCATOR
; ================================

section .bss align=4096
next_free_page:  resq 1        ; stores next free 4KB page

section .text
global alloc_page

; Returns in RAX the physical address of a free 4KB page
alloc_page:
    ; Initialize next_free_page if zero (lazy init)
    mov rax, [next_free_page]
    cmp rax, 0
    jne .has_next

    ; First free page: start after the kernel identity map (1GB)
    mov rax, 0x40000000       ; 1GB
    mov [next_free_page], rax

.has_next:
    ; Return current free page
    mov rax, [next_free_page]

    ; Increment to point to next free 4KB page
    add rax, 0x1000           ; 4KB
    mov [next_free_page], rax

    ret

; ================================
; USER MODE SWITCH
; ================================

switch_to_user_task:
    ; rdi = RIP
    ; rsi = RSP

    push 0x23
    push rsi
    pushfq
    push 0x1B
    push rdi

    iretq

; ================================
; SYSCALL ENTRY
; ================================

syscall_entry:

    pushRegs

    ; syscall ABI:
    ; rax = syscall number
    ; rdi,rsi,rdx,r10,r8,r9 = args

    mov rdi,rax
    mov rsi,rdi
    mov rdx,rsi
    mov rcx,rdx
    mov r8,r10
    mov r9,r8

    call syscall_dispatch

    popRegs

    iretq
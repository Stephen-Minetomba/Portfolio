void root_task() {
    __asm__ volatile (
        "mov $1, %%rax\n\t"  // syscall number 1 = exit
        "xor %%rdi, %%rdi\n\t" // exit code 0
        "syscall\n\t"
        :
        :
        : "rcx", "r11", "memory"
    );
}
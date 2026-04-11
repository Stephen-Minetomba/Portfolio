#include "stdint.h"
#include "stddef.h"

// AI USED IN THE GENERATION OF COMMENTS IN THIS CODE

// ---------- CONFIG ----------
#define STACK_SIZE 4096
#define MAX_TASKS 8
#define SYSCALL_MAX 128
#define HEAP_SIZE 65536 // 64 KB heap
#define HEAP_PER_TASK HEAP_SIZE/MAX_TASKS

// ---------- TASK STRUCT ----------
uint8_t task_heap[MAX_TASKS][HEAP_PER_TASK];
typedef struct {
    uint64_t rip;       // instruction pointer
    uint64_t rsp;       // stack pointer
    uint64_t cr3;       // page table
    int status;         // 0 = dead, 1 = active
    int exitcode;       // 0 = success, 1 = error, 2 = running
} user_task_t;

// ---------- GLOBALS ----------
long current_task = 0;
int64_t num_tasks = 0;

user_task_t tasks[MAX_TASKS];
uint8_t user_stacks[MAX_TASKS][STACK_SIZE];

// ---------- IPC / MAILBOX ----------
long mailboxes[MAX_TASKS][2]; // [0] = public writable, [1] = read-only for everyone

// ---------- SYSCALLS ----------
typedef long (*syscall_fn_t)(long, long, long, long, long, long);
syscall_fn_t syscall_table[SYSCALL_MAX];

// ---------- EXTERNAL ----------
extern void switch_to_user_task(uint64_t rip, uint64_t rsp);

// ---------- SCHEDULER ----------
void kernel(void) {
    while (1) __asm__ volatile("hlt");
}

void schedule(void) {
    for (int i = 0; i < num_tasks; i++) {
        current_task = (current_task + 1) % num_tasks;

        if (tasks[current_task].status == 1) {
            switch_to_user_task(tasks[current_task].rip, tasks[current_task].rsp);
            return;
        }
    }
    kernel(); // no tasks alive
}

// ---------- DYNAMIC MEMORY ----------
uint8_t kernel_heap[HEAP_SIZE];
typedef struct mem_block {
    size_t size;
    struct mem_block* next;
} mem_block_t;

mem_block_t* free_list = NULL;

void init_heap(void) {
    free_list = (mem_block_t*)kernel_heap;
    free_list->size = HEAP_SIZE - sizeof(mem_block_t);
    free_list->next = NULL;
}

// ---------- TASK CREATION ----------
int create_task(void (*entry)()) {
    if (num_tasks >= MAX_TASKS) return 1; // no free slot left

    int id = num_tasks;

    tasks[id].rip = (uint64_t)entry;
    tasks[id].rsp = (uint64_t)(user_stacks[id] + STACK_SIZE);
    tasks[id].status = 1;
    tasks[id].exitcode = 2;

    // initialize mailboxes
    mailboxes[id][0] = 0;
    mailboxes[id][1] = 0;

    num_tasks++;
    return 0;
}

// ------- FORWARD DECLARATION -------
long syscall_dispatch(long nr, long a1, long a2, long a3, long a4, long a5);

// -------------- TASKS --------------

// useless task (no offense)
void task0(void) {
    syscall_dispatch(1,0,0,0,0,0);
}

#include "init.c"

// ---------- INIT ----------
void init_tasks(void) {
    init_heap();
    create_task(task0);
    create_task(root_task);
}

// ---------- SYSCALL IMPLEMENTATIONS ----------
long sys_exit(long code, long a2, long a3, long a4, long a5, long a6) {
    tasks[current_task].status = 0;
    tasks[current_task].exitcode = code;
    return 0;
}

long sys_malloc(long size, long a2, long a3, long a4, long a5, long a6) {
    size = (size + 7) & ~7; // align 8 bytes

    mem_block_t* prev = NULL;
    mem_block_t* curr = free_list;

    while (curr) {
        if (curr->size >= (size_t)size) {
            if (curr->size > size + sizeof(mem_block_t)) {
                mem_block_t* next_block = (mem_block_t*)((uint8_t*)curr + sizeof(mem_block_t) + size);
                next_block->size = curr->size - size - sizeof(mem_block_t);
                next_block->next = curr->next;

                if (prev) prev->next = next_block;
                else free_list = next_block;

                curr->size = size;
            } else {
                if (prev) prev->next = curr->next;
                else free_list = curr->next;
            }
            return (long)((uint8_t*)curr + sizeof(mem_block_t));
        }
        prev = curr;
        curr = curr->next;
    }

    // no memory left (so... what do you do? you kill the task)
    tasks[current_task].status = 0;
    tasks[current_task].exitcode = 1;
    return 0;
}

long sys_free(long ptr_addr, long a2, long a3, long a4, long a5, long a6) {
    if (!ptr_addr) return 0;

    mem_block_t* block = (mem_block_t*)(ptr_addr - sizeof(mem_block_t));
    block->next = free_list;
    free_list = block;

    return 0;
}

long sys_send(long message, long task_id, long mailbox, long a4, long a5, long a6) {
    if (task_id < 0 || task_id >= num_tasks || mailbox < 0 || mailbox > 1) {
        tasks[current_task].status = 0;
        tasks[current_task].exitcode = 1;
        return 1;
    }

    if (mailbox == 0) {
        mailboxes[task_id][0] = message;
        return 0;
    } else {
        if (current_task == task_id) {
            mailboxes[task_id][mailbox] = message;
        }else {
            tasks[current_task].status = 0;
            tasks[current_task].exitcode = 1;
            return 1;
        }
    }
}

long sys_receive(long task_id, long mailbox, long a3, long a4, long a5, long a6) {
    if (task_id < 0 || task_id >= num_tasks || mailbox < 0 || mailbox > 1) {
        tasks[current_task].status = 0;
        tasks[current_task].exitcode = 1;
        return 1;
    }
    return mailboxes[task_id][mailbox];
}

long spc_fork(long func_ptr, long a2, long a3, long a4, long a5, long a6) {
    if (current_task != 1) {
        tasks[current_task].status = 0;
        tasks[current_task].exitcode = 1;
        return 1; // error
    }
    void (*location)() = (void(*)())func_ptr;
    return create_task(location);
}

long sys_getpid(long a1, long a2, long a3, long a4, long a5, long a6) {
    return current_task;
}

long spc_in8(long port, long a2, long a3, long a4, long a5, long a6) {
    if (current_task != 1) {
        tasks[current_task].status = 0;
        tasks[current_task].exitcode = 1;
        return -1; // error (it uses -1 because I/O ports can/usually only hold unsigned values but the 'long' C type can store negative values too)
    }
    unsigned char value;
    __asm__ volatile (
        "inb %%dx, %%al"
        : "=a"(value)
        : "d"(port)
    );

    return (long)value;
}

long spc_in16(long port, long a2, long a3, long a4, long a5, long a6) {
    if (current_task != 1) {
        tasks[current_task].status = 0;
        tasks[current_task].exitcode = 1;
        return -1; // error (it uses -1 because I/O ports can/usually only hold unsigned values but the 'long' C type can store negative values too)
    }
    unsigned char value;
    __asm__ volatile (
        "inw %%dx, %%ax"
        : "=a"(value)
        : "d"(port)
    );

    return (long)value;
}

long spc_in32(long port, long a2, long a3, long a4, long a5, long a6) {
    if (current_task != 1) {
        tasks[current_task].status = 0;
        tasks[current_task].exitcode = 1;
        return -1; // error (it uses -1 because I/O ports can/usually only hold unsigned values but the 'long' C type can store negative values too)
    }
    unsigned char value;
    __asm__ volatile (
        "inl %%dx, %%eax"
        : "=a"(value)
        : "d"(port)
    );

    return (long)value;
}

long spc_out8(long port, long value, long a3, long a4, long a5, long a6) {
    if (current_task != 1) {
        tasks[current_task].status = 0;
        tasks[current_task].exitcode = 1;
        return -1; // error (it uses -1 because I/O ports can/usually only hold unsigned values but the 'long' C type can store negative values too)
    }
    // Only the low 8 bits of value are sent (like 'outb')
    __asm__ volatile (
        "outb %%al, %%dx"
        :
        : "a"(value), "d"(port)
    );
    return 0;
}

long spc_out16(long port, long value, long a3, long a4, long a5, long a6) {
    if (current_task != 1) {
        tasks[current_task].status = 0;
        tasks[current_task].exitcode = 1;
        return -1; // error (it uses -1 because I/O ports can/usually only hold unsigned values but the 'long' C type can store negative values too)
    }
    __asm__ volatile (
        "outw %%ax, %%dx"
        :
        : "a"(value), "d"(port)
    );
    return 0;
}

long spc_out32(long port, long value, long a3, long a4, long a5, long a6) {
    if (current_task != 1) {
        tasks[current_task].status = 0;
        tasks[current_task].exitcode = 1;
        return -1; // error (it uses -1 because I/O ports can/usually only hold unsigned values but the 'long' C type can store negative values too)
    }
    __asm__ volatile (
        "outl %%eax, %%dx"
        :
        : "a"(value), "d"(port)
    );
    return 0;
}

long spc_kill(long process, long a2, long a3, long a4, long a5, long a6) {
    if (current_task != 1) {
        tasks[current_task].status = 0;
        tasks[current_task].exitcode = 1;
        return -1; // error (it uses -1 because I/O ports can/usually only hold unsigned values but the 'long' C type can store negative values too)
    }
    tasks[process].status = 0;
    tasks[process].exitcode = 1;
    return 0;
}

// --------------------
// SPECIAL MEMORY MANAGEMENT
// --------------------
long spc_steal(long process, long addr, long a3, long a4, long a5, long a6) {
    if (current_task != 1) return -1;
    if (process < 0 || process >= num_tasks || tasks[process].status == 0) return -1;
    uint8_t* heap_start = task_heap[process];
    uint8_t* heap_end   = heap_start + HEAP_PER_TASK;
    uint8_t* ptr = (uint8_t*)(intptr_t)addr;
    if (ptr < heap_start || ptr >= heap_end) return -1;
    return (long)(*ptr);
}

// ---------- SYSCALL SETUP ----------
void init_syscalls() {
    syscall_table[1] = sys_exit;
    syscall_table[2] = sys_send;
    syscall_table[3] = sys_receive;
    syscall_table[4] = sys_malloc;
    syscall_table[5] = sys_free;
    syscall_table[6] = spc_fork;
    syscall_table[7] = sys_getpid;
    syscall_table[8] = spc_in8;
    syscall_table[9] = spc_in16;
    syscall_table[10] = spc_in32;
    syscall_table[11] = spc_out8;
    syscall_table[12] = spc_out16;
    syscall_table[13] = spc_out32;
    syscall_table[14] = spc_kill;
    syscall_table[15] = spc_steal;
}
// SPC = "SPeCial" syscalls that only PID 1 can call
// SYS = "SYStem" syscalls that any process can call

long syscall_dispatch(long nr, long a1, long a2, long a3, long a4, long a5) {
    if (nr < 0 || nr >= SYSCALL_MAX || !syscall_table[nr])
        return -1;
    return syscall_table[nr](a1, a2, a3, a4, a5, 0);
}

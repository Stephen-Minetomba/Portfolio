# Syscalls
## SYS
### Process utilities
#### EXIT
##### Syscall ID: 1
##### Description: Kills current process.
##### Returns: 0
#### GETPID
##### Syscall ID: 7
##### Description: Gets PID of current process.
##### Returns: PID
### Memory management
#### MALLOC
##### Syscall ID: 4
##### Description: Allocates memory.
##### Returns: Address of that space (usable in a pointer).
#### FREE
##### Syscall ID: 5
##### Description: Frees memory previously allocated using malloc.
##### Returns: 0
### IPC/Inter-process communication
#### SEND
##### Syscall ID: 2
##### Description: Puts the specified value inside the specified task's specified mailbox.
##### Returns: 0
#### RECEIVE
##### Syscall ID: 3
##### Description: Gets contents of the specified mailbox of the specified task.
##### Returns: Value inside mailbox, or 1 for an out-of-bounds error.
## SPC/Special (accessible only by PID 1)
### Input
#### IN8
##### Syscall ID: 8
##### Description: 8-bit wrapper around the 'inb' assembly function. Uses the 'al' register.
##### Returns: Value of that port.
#### IN16
##### Syscall ID: 9
##### Description: 16-bit wrapper around the 'inw' assembly function. Uses the 'ax' register.
##### Returns: Value of that port.
#### IN32
##### Syscall ID: 10
##### Description: 32-bit wrapper around the 'inl' assembly function. Uses the 'eax' register.
##### Returns: Value of that port.
### Output
#### OUT8
##### Syscall ID: 11
##### Description: 8-bit wrapper around the 'outb' assembly function. Uses the 'al' register.
##### Returns: Value of that port.
#### OUT16
##### Syscall ID: 12
##### Description: 16-bit wrapper around the 'outw' assembly function. Uses the 'ax' register.
##### Returns: Value of that port.
#### OUT32
##### Syscall ID: 13
##### Description: 32-bit wrapper around the 'outl' assembly function. Uses the 'eax' register.
##### Returns: Value of that port.
### Special process management
#### FORK
##### Syscall ID: 6
##### Description: Launches a new process at the specified function location.
##### Returns: 1 if no slots are left, 0 for success.
#### KILL
##### Syscall ID: 14
##### Description: Kills the specified process.
##### Returns: 0
### Special memory management
#### STEAL
##### Syscall ID: 15
##### Description: Steals the value at the specified memory address of the specified process.
##### Returns: Value.
# Global process management
## The structure of each process
### PID/Process identification number
#### Description: The number assigned to that process.
### RIP & RSP
#### Description: Instruction pointer, stack pointer.
### STATUS
#### Description: 0 = dead, 1 = active
### EXIT CODE
#### Description: 0 = success, 1 = error, 2 = running
## Scheduler
### Description: A round-robin scheduler.
### Pros:
#### Selects the next task fairly.
#### No prioritized/underprioritized tasks.
### Cons:
#### Doesn't allow for a 'yield' syscall easily (not because of the scheduler, it's because of the rule "Only the timer interrupt must call schedule() and nothing else").
# Miscellaneous
## Rules
### Scheduler must only be called by the timer interrupt to avoid confusion.
## Brutality against syscall abuse
### Any process that causes an "out-of-bounds" error will get killed immediately.
## Messaging boxes
### Each process has two boxes:
#### The read-only box is accessible only by the owning process of it.
#### The write-only box is accessible by any process.
### Future boxes (which also must add new syscalls):
#### Whitelist box (will add a "whitelist <PID>" and "remove_from_whitelist" syscall) is writable only by the approved processes.
## Security features
### Mutual consent is needed to communicate between processes
#### Pros:
##### Extreme security because it is combined with the "absolute isolation" feature.
#### Cons:
##### Wastes a few CPU cycles (a few nanoseconds).
### Absolute isolation (well... kinda)
#### Pros:
##### The only way to attack/communicate is through mailboxes (and files if PID 1 sets up files too)
#### Cons:
##### None
### The only attack vectors:
#### Through a rogue process exploiting vulnerabilities in the implementation of syscalls to get ring0 access.
#### Gaining access to PID 1 by exploiting a vulnerability inside it (since it's the one with SPC calls).
#### Exploiting the mailing system to gain access to PID 1.
### There's a maximum amount of processes (defined in the source code).
### Debuggers are impossible to implement unless PID 1 provides hooks.
# Startup
## EFI_MAIN (full asm) > KERNEL STACK (full asm) > EXIT_BOOT_SERIVCES (full asm) > INIT GDT (full asm) > INIT IDT (asm) > INIT PAGING (full asm) > INIT TASKS (asm-C) > INIT HEAP (full C) > CREATION OF TASKS (full C) > INIT SYSCALLS (asm-C)
## TIMER INTERRUPT (full asm) > SCHEDULER (full C)
# Mail handshake
## If you don't know the PID and want the process to listen:
```Conversation (notice how it loops over the processes? it is because of the round-robin scheduler)
PID 1: fork(<location of the PID 2 function>)
PID 2: mov rax, rax (waste)
PID 1: fork(<location of the PID 3 function>)
PID 2: send(2, 3, 0) // message (I am PID 2), task (to PID 3), mailbox (the "write" box of PID 3)
PID 3: whitelist(receive(3, 0))
PID 1: mov rax, rax (waste)
PID 2: whitelist(3)
// HANDSHAKE COMPLETE
```
## If you know the PID (a lot more stable and predictable... if you know the PID):
```Conversation
PID 1: fork(<location of the PID 2 function>)
PID 2: mov rax, rax (waste)
PID 1: fork(<location of the PID 3 function>)
PID 2: whitelist(3)
PID 3: whitelist(2)
PID 1: mov rax, rax (waste)
// HANDSHAKE COMPLETE
```

# Information
Name: Blizzard
Arch: Harvard, 64-bit
Formal name: H_Blizzard_64_F

## Formal name breakdown
_ is a separator
H specifies "Harvard architecture", can also be V for "Von Neumman Architecture". Tip: Make a memory adapter that exposes a second read interface for the main RAM, plug it into the ports made for the flash memory, and you got yourself Von Neumman architecture on a Harvard computer.
64 specifies the bit size (64 bits)
F specifies the instruction set, in this case, it stands for "Forth"

# Stack configuration
data_stack[10]

# RAM configuration
Maximum recommended: 1 billion gigabytes (1 exabyte)
The absolute addressable maximum: 9,223,372,036,854,775,807 bits of RAM
Each memory value, at each address, is 64 bits. That means, if the CPU addresses the value at address 2, it should receive a 64-bit integer located at that memory address.

# Main functions
1. top() | Peek at the top of the data stack
2. pop() | Peek at the top of the data stack, and then remove that item
3. push(value) | Push that value to the data stack

# Instruction set
1. ADD void | push(pop() + pop())
2. LSH void | push(pop() << 1)
3. NOR void | push(~(pop() | pop()))
4. LDI immediate | push(*(pc + 1)); pc += 1
5. JL void | if (pop() < pop()) pc = pop()
6. @ void | push(*pop())
7. ! void | *pop() = pop()
8. DUP void | push(top())
9. SWAP void | v1 = pop(); v2 = pop(); push(v1); push(v2)
10. DROP void | pop()
11. PC void | push(pc);

# Macros
## JUMP UNCONDITIONALLY (works)
arguments: <address>
commands (from top to bottom):
- LDI <address>
- LDI 0
- LDI 1
- JL

## CALL (untested)
arguments: <address to store return address> <target address>
- PC
- LDI <address to store return address>
- !
- LDI <target address>
- LDI 0
- LDI 1
- JL

## RETURN (untested)
arguments: <address storing return address>
- LDI <address storing return address>
- @
- LDI 0
- LDI 1
- JL

## JUMP IF GREATER THAN (works)
arguments: <value A> <value B> <address>
- LDI <address>
- LDI <value A>
- LDI <value B>
- JL

## NEGATIVE/SIGN (works)
arguments: <value>
- LDI <value>
- LDI 0
- NOR
- LDI 1
- ADD

# Examples
## Infinite loop (works)
Source code: 0 JMP
## 2 plus 2 (works)
Source code: 2 2 +
## 3 minus 1 (works)
Source code: 3 1 NEG +
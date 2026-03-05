# Instructions:
# immediate
## LDI <result register>,<number> | rA = B
## ADDI <input register>,<number>,<result register> | rC = rA + B
# registers
## NAND <input register>,<input register>,<result register> | Does a NAND gate between these registers and outputs the result in the result register
## INV <input register>,<result register> | Inverts (e.g. from -1 to 1, or from 1 to -1)
## ADD <input register>,<input register>,<result register> | rC = rA + rB
## MOV <input register>,<result register> | rB = rA
# branching
## CMP <input register>,<input register>
## JNE <register storing instruction index> | Jump if not equal
## JE <register storing instruction index> | Jump if equal
## JG <register storing instruction index> | Jump if greater
## JS <register storing instruction index> | Jump if smaller
## JGE <register storing instruction index> | Jump if greater or equal
## JSE <register storing instruction index> | Jump if smaller or equal
## JMP <register storing instruction index> | Jump unconditionally
# functions
## CALL <name> | Jumps to that function unconditionally
## RET | Return
## >name | Defines a function named 'name' (will not get executed unless called. These are not the same things as labels)
## <name | Similar to a closing bracket
# memory
## TAKE <address> <result register> | Overwrites that register with what content is stored in that address
## PUT <address> <input register> | Overwrites that memory address with the contents of the input register
# indirect operations
## MOVP <register storing the index of the input register>,<register storing the index of the result register> | rrB = rrA

flash = [
    "ldi r1,5",
    "call double",
    "ldi r2,7",
    "jmp r2",

    ">double",
    "add r1,r1,r1",
    "ret",
    "<double"
]

memory = [0] * 128
registers = [0] * 32

pc = 0
flag_eq = False
flag_gt = False
flag_lt = False
call_stack = []

functions = {}

for i, inst in enumerate(flash):
    if inst.startswith(">"):
        name = inst[1:]
        functions[name] = i + 1

def find_function_end(name, start):
    for i in range(start, len(flash)):
        if flash[i] == f"<{name}":
            return i
    return start

while pc < len(flash):

    inst = flash[pc]
    parts = inst.replace(",", " ").split()

    if not parts:
        pc += 1
        continue

    op = parts[0]

    if op.startswith(">"):
        name = op[1:]
        pc = find_function_end(name, pc) + 1
        continue

    if op.startswith("<"):
        pc += 1
        continue

    if op == "ldi":
        r = int(parts[1][1:])
        value = int(parts[2])
        registers[r] = value

    elif op == "add":
        ra = int(parts[1][1:])
        rb = int(parts[2][1:])
        rc = int(parts[3][1:])
        registers[rc] = registers[ra] + registers[rb]

    elif op == "addi":
        ra = int(parts[1][1:])
        value = int(parts[2])
        rc = int(parts[3][1:])
        registers[rc] = registers[ra] + value

    elif op == "nand":
        ra = int(parts[1][1:])
        rb = int(parts[2][1:])
        rc = int(parts[3][1:])
        registers[rc] = ~(registers[ra] & registers[rb])

    elif op == "inv":
        ra = int(parts[1][1:])
        rc = int(parts[2][1:])
        registers[rc] = registers[ra] * -1

    elif op == "mov":
        ra = int(parts[1][1:])
        rb = int(parts[2][1:])
        registers[rb] = registers[ra]

    elif op == "movp":
        ra = int(parts[1][1:])
        rb = int(parts[2][1:])

        src = registers[ra]
        dst = registers[rb]

        registers[dst] = registers[src]

    elif op == "cmp":
        ra = int(parts[1][1:])
        rb = int(parts[2][1:])
        a = registers[ra]
        b = registers[rb]

        flag_eq = a == b
        flag_gt = a > b
        flag_lt = a < b

    elif op == "jne":
        r = int(parts[1][1:])
        if not flag_eq:
            pc = registers[r]
            continue

    elif op == "je":
        r = int(parts[1][1:])
        if flag_eq:
            pc = registers[r]
            continue

    elif op == "jg":
        r = int(parts[1][1:])
        if flag_gt:
            pc = registers[r]
            continue

    elif op == "js":
        r = int(parts[1][1:])
        if flag_lt:
            pc = registers[r]
            continue

    elif op == "jge":
        r = int(parts[1][1:])
        if flag_gt or flag_eq:
            pc = registers[r]
            continue

    elif op == "jse":
        r = int(parts[1][1:])
        if flag_lt or flag_eq:
            pc = registers[r]
            continue

    elif op == "jmp":
        r = int(parts[1][1:])
        pc = registers[r]
        continue

    elif op == "call":
        name = parts[1]

        call_stack.append(pc + 1)
        pc = functions[name]
        continue

    elif op == "ret":
        if call_stack:
            pc = call_stack.pop()
        else:
            break
        continue

    elif op == "take":
        addr = int(parts[1])
        r = int(parts[2][1:])
        registers[r] = memory[addr]

    elif op == "put":
        addr = int(parts[1])
        r = int(parts[2][1:])
        memory[addr] = registers[r]

    pc += 1

print(registers)
# Welcome to the BitLang programming language! You can either code manually or use the compiler (which is a lot easier).

# Instruction memory
program = input("Program: ")


# Memory: 1024 bits (128 bytes)
cells = [0] * 1024

# Cell pointer stored in a register
cell_pointer = 0

# Instruction pointer stored in a program counter (PC) register
instruction_pointer = 0

# Precompute matching brackets/braces
bracket_map = {}
stack = []

for i, cmd in enumerate(program):
    if cmd in ["[", "{", "("]:
        stack.append((cmd, i))  # store both type and position
    elif cmd in ["]", "}", ")"]:
        if not stack:
            raise ValueError(f"No matching opening for '{cmd}' at position {i}")
        open_cmd, start = stack.pop()
        if (open_cmd == "[" and cmd != "]") or (open_cmd == "{" and cmd != "}") or (open_cmd == "(" and cmd != ")"):
            raise ValueError(f"Mismatched '{open_cmd}' and '{cmd}' at position {i}")
        bracket_map[start] = i  # link open -> close
        bracket_map[i] = start  # link close -> open

if stack:
    raise ValueError(f"No matching closing for '{stack.pop()[0]}'")

# Program execution
while instruction_pointer < len(program):
    cmd = program[instruction_pointer]

    if cmd == ">":
        cell_pointer = (cell_pointer + 1) % len(cells)
    elif cmd == "<":
        cell_pointer = (cell_pointer - 1) % len(cells)
    elif cmd == "T":
        cells[cell_pointer] ^= 1
    elif cmd == ".":
        print(cells[cell_pointer], end="")
    elif cmd == ",":
        while True:
            text = input("\nInput 0 or 1: ")
            if text in ("0", "1"):
                cells[cell_pointer] = int(text)
                break
    elif cmd == "[":
        if cells[cell_pointer] == 0:
            instruction_pointer = bracket_map[instruction_pointer]
    elif cmd == "]":
        if cells[cell_pointer] != 0:
            instruction_pointer = bracket_map[instruction_pointer]
    elif cmd == "{":
        # Execute block only if current cell is zero
        if cells[cell_pointer] != 0:
            instruction_pointer = bracket_map[instruction_pointer]
    elif cmd == "}":
        # Nothing to do; just part of the if-block
        pass
    elif cmd == "(":
        # Execute block only if current cell is one
        if cells[cell_pointer] == 0:
            instruction_pointer = bracket_map[instruction_pointer]
    elif cmd == ")":
        pass
    elif cmd == "E":
        exit(0)

    # print("---")
    # print(f"New cell pointer: {str(cell_pointer)}")
    # print(f"Command executed: {str(cmd)}")
    # print(cells[:4])
    # print("---")

    instruction_pointer += 1

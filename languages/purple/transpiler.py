pseudocode = []

# Moving
def mov(x: int, y: int): # Register to be set, Register containing value
    pseudocode.append(f"r{x} = r{y} // MOV r{x} r{y}")
    return f"purple i{x} r{y} i0==i0 0"
def movi(x: int, y: int): # Register to be set, Integer
    pseudocode.append(f"r{x} = {y} // MOVI r{x} {y}")
    return f"purple i{x} i{y} i0==i0 0"
def pmov(x: int, y: int): # Register containing value that points to the register to be set, Register containing value
    pseudocode.append(f"r[{x}] = r{y} // PMOV r{x} r{y}")
    return f"purple r{x} r{y} i0==i0 0"

# Operations
def add(x: int, y: int): # Register to be set, Register containing value
    pseudocode.append(f"r{x} += r{y} // ADD r{x} r{y}")
    return f"purple i{x} r{y} i0==i0 1"
def padd(x: int, y: int): # Register containing value that points to the register to be set, Register containing value
    pseudocode.append(f"r[{x}] += r{y} // PADD r{x} r{y}")
    return f"purple r{x} r{y} i0==i0 1"
def addi(x: int, y: int): # Register to be set, Integer
    pseudocode.append(f"r{x} += {y} // ADDI r{x} {y}")
    return f"purple i{x} i{y} i0==i0 1"

# Branching
def jmp(x: int, condition: str): # Register containing value, Condition
    pseudocode.append(f"// JMP r{x} {condition}")
    return f"purple i0 r{x} {condition} 0"
def jmpi(x: int, condition: str): # Integer, Condition
    pseudocode.append("} loop if " + condition + " // JMPI " + f"{x} {condition}")
    pseudocode.insert(x + 1, "do {")
    index = x + 2
    while index < len(pseudocode) - 1:
        pseudocode[index] = "\t" + pseudocode[index]
        index += 1
    return f"purple i0 i{x} {condition} 0"

program = [
    movi(1, 7),
    movi(2, 1),
    movi(3, 1),
    mov(5, 3),
    movi(4, 0),
    add(3, 5),
    addi(4, 1),
    jmpi(4, "r4!=r2"),
    addi(2, 1),
    jmpi(2, "r2!=r1")
]
print('\n'.join(program) + "\n")
print("PURPLE SYNTAX")
print("-----")
print("PSEUDOCODE SYNTAX\n")
print('\n'.join(pseudocode))

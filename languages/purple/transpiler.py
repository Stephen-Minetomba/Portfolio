pseudocode = []

# Moving
def mov(x: int, y: int): # Register to be set, Register containing value
    pseudocode.append(f"r{x} = r{y} // MOV r{x} r{y}")
    return f"purple i{x} r{y} i0==i0 0 0"
def movi(x: int, y: int): # Register to be set, Integer
    pseudocode.append(f"r{x} = {y} // MOVI r{x} {y}")
    return f"purple i{x} i{y} i0==i0 0 0"
def pmov(x: int, y: int): # Register containing value that points to the register to be set, Register containing value
    pseudocode.append(f"r[{x}] = r{y} // PMOV r{x} r{y}")
    return f"purple r{x} r{y} i0==i0 0 0"

# Operations
def add(x: int, y: int, invert: bool = False): # Register to be set, Register containing value, Boolean specifying whether it should invert B on runtime
    pseudocode.append(f"r{x} += {'invert(' if invert else ''}r{y}{')' if invert else ''} // ADD r{x} r{y} {int(invert)}")
    return f"purple i{x} r{y} i0==i0 1 {int(invert)}"
def padd(x: int, y: int, invert: bool = False): # Register containing value that points to the register to be set, Register containing value, Boolean specifying whether it should invert B on runtime
    pseudocode.append(f"r[{x}] += {'invert(' if invert else ''}r{y}{')' if invert else ''} // PADD r{x} r{y} {int(invert)}")
    return f"purple r{x} r{y} i0==i0 1 {int(invert)}"
def addi(x: int, y: int, invert: bool = False): # Register to be set, Integer, Boolean specifying whether it should invert B on runtime
    pseudocode.append(f"r{x} += {'invert(' if invert else ''}{y}{')' if invert else ''} // ADDI r{x} {y} {int(invert)}")
    return f"purple i{x} i{y} i0==i0 1 {int(invert)}"

# Branching
def jmp(x: int, condition: str): # Register containing value, Condition
    pseudocode.append(f"// JMP r{x} {condition}")
    return f"purple i0 r{x} {condition} 0 0"
def jmpi(x: int, condition: str): # Integer, Condition
    pseudocode.append("} jump back if " + condition + " // JMPI " + f"{x} {condition}")
    pseudocode.insert(x + 1, "do {")
    index = x + 2
    while index < len(pseudocode) - 1:
        pseudocode[index] = "\t" + pseudocode[index]
        index += 1
    return f"purple i0 i{x} {condition} 0 0"

program = [
    movi(1, 7),
    addi(1, 3, True)
]
print('\n'.join(program) + "\n")
print("PURPLE SYNTAX")
print("-----")
print("PSEUDOCODE SYNTAX\n")
print('\n'.join(pseudocode))

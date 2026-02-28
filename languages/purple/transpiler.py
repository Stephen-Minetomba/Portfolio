code = """
r1 = 5
r2 = 5
r3 = 0
r4 = 0
while not r3==r1 {
    r4 += r2
    r3 ++
}
"""

# Notes:
# 1. No indentation needed
# 2. {} needed for while loops (one on the same line as the while loop, and one standalone bracket when you end the loop)
# 3. No ; needed at the end of a line
# 4. Comments are made using //
# 5. No : needed at the end of a while loop

# Turn code into lines
code = code.splitlines()

# Preprocessor: remove comments and empty lines
processed_code = []
for line in code:
    l = str(line)
    while "\t" in l or "  " in l:
        l = l.strip("\t").strip("  ")
    l = l.split("//")[0].rstrip()
    if l != "":
        processed_code.append(l)

# Transpiler 1: turn that code into an assembly-like language that can be converted to purple
assembly = []
loop_stack = []
i = 0
while i < len(processed_code):
    line = processed_code[i]
    if line.startswith("while not"):
        cond = line[len("while not"):].strip().rstrip("{")
        loop_start = len(assembly)
        loop_end = None
        loop_stack.append((loop_start, cond))
        assembly.append(f"JMPI ? {cond}")
        i += 1
        continue
    if line == "}":
        if loop_stack:
            loop_start, cond = loop_stack.pop()
            loop_end = len(assembly)
            assembly[loop_start] = f"JMPI {loop_end} {cond}"
            assembly.append(f"JMPI {loop_start - 1} i0==i0")
        i += 1
        continue
    if line.endswith("++"):
        reg = line.replace("++", "")
        assembly.append(f"ADDI {reg.strip("r").strip("i")} 1")
    elif line.endswith("--"):
        reg = line.replace("--", "")
        assembly.append(f"ADDI {reg.strip("r").strip("i")} -1")
    elif "+=" in line or "-=" in line:
        if "+=" in line:
            reg, val = line.split("+=")
            op = "ADD"
        else:
            reg, val = line.split("-=")
            op = "SUB"
        reg = reg.strip()
        val = val.strip()
        type_of_instruction = op if val.startswith("r") else f"{op}I"
        assembly.append(f"{type_of_instruction} {reg.strip("r").strip("i")} {val.strip("r").strip("i")}")
    elif "=" in line:
        reg, val = line.split("=")
        reg = reg.strip()
        val = val.strip()
        type_of_instruction = "MOV" if val.startswith("r") else "MOVI"
        assembly.append(f"{type_of_instruction} {reg.strip("r").strip("i")} {val.strip("r").strip("i")}")
    elif str(line).lower().startswith("goto"):
        parameters = str(line).split(" ")
        to = parameters[1].strip()
        condition = parameters[2].strip()
        if not to.startswith("r"):
            raise ValueError("Must specify a register (error in goto). Goto is made to make dynamic jumping possible (which makes implemented 'call' and 'return' a lot easier)")
        to = str(int(to[1:])) # It may seem like a waste of instructions to do this, but I am doing this so that it raises a value error in case it is not a number
        assembly.append(f"PJMP r{to} {condition}")
    elif line.lower().startswith("pval"): # Register holding the index of the register that should be set to the register specified in the second argument
        parameters = [i.strip() for i in str(line).split(" ")]
        assembly.append(f"PMOV {parameters[1]} {parameters[1]}")
    else:
        raise ValueError(f"Unknown instruction: {line}")
    i += 1
assembly = [" ".join(l.split()) for l in assembly]
print("\n".join(assembly))

# Transpiler 2: turn that assembly-like language into purple
# Argument types: V = integer (value), S = string
table = {
    "MOVI": "purple iV iV i0==i0 0 0",
    "MOV": "purple iV rV i0==i0 0 0",
    "PMOV": "purple rV rV i0==i0 0 0",
    "JMPI": "purple i0 iV S 0 0",
    "PJMP": "purple i0 rV S 0 0",
    "ADDI": "purple iV iV i0==i0 1 0",
    "ADD": "purple iV rV i0==i0 1 0",
    "SUBI": "purple iV iV i0==i0 1 1",
    "SUB": "purple iV rV i0==i0 1 1"
}

purple = []

for instruction in assembly:
    parameters = [inst.strip() for inst in instruction.split(" ")]
    target = table[parameters[0]]
    order = [i for i in target if i in ("S", "V")]
    if not len(parameters) - 1 == len(order):
        raise ValueError("Invalid length")
    for idx, parameter in enumerate(parameters[1:]):
        par = ""
        try:
            _test = int(parameter)
            par = "V"
        except ValueError:
            par = "S"
        needed = order[idx]
        if needed == par:
            target = target.replace(needed, str(parameter), 1)
        else:
            raise ValueError(f"Invalid argument type.\nExpected:{needed}\nReceived:{par}")
    purple.append(target)
print("\n".join(purple))
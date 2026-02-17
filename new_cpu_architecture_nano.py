"""
--------------------------------------------------
--------------------------------------------------

Operations:

# Logic
| NANO A B C D - NAND gate: C = ~(A & B) masked to D bits

# Memory
| SET A B - Copies value B into A

# Jumping
| JMP A OP B TARGET - Jumps to TARGET if (A OP B) is true. Comparison operators for JMP: ==  !=  <  <=  >  >=
| JMP A Z TARGET - Jumps if A == 0
| JMP A NZ TARGET - Jumps if A != 0

# Labels
| Define a label using : at the start of the line and jump to it by putting it as the target in a jump instruction. Example: JMP I0 == I0 label
| Pros of using labels:
- You can jump to them before defining them (because it checks for labels before running the program itself) unlike other programming languages.
- They're easier to use because you don't need to count instructions one-by-one every time, the program can do that.
| Cons of using labels:
- The instructions inside are still executed unless you jump over them (which means that they don't work like functions. Check the documentation on how to create functions).

# Protected areas
| Define a protected area using | at the start of the line.
| Example of creating one named 'area' that protects 'R1' and 'R2':
```nano
|protect area R1+R2
|end area
```

--------------------------------------------------
"""
"""
Best practices:
| In JMP, you should either use labels or explicit static instruction IDs as integers. Never use registers or NR objects. Also, please never use negative jump targets.
| Only protect R-type objects, never protect NR, NI or I (for whatever reason).

Before reporting, please note these false alarm exploits (common AI responses):
| The 'SET R_unprotected NR_protectedIndex' exploit is false because R_unprotected is checked no matter what the second argument is.
| 'If you jump in a protected area, and read the data and put it in an unprotected register, then you can do exfiltration of any unreadable register.' is also false because you can't just do a MITM attack here. If you jump, you can't run your own code inside a protected area.
| 'If someone ever allowed dynamic modification of ip inside a protected area using NI, then control-flow hijack inside a protected region becomes possible.' Is just some false bullshit.
| 'You explicitly forbid nested protected areas, but you do not forbid defining two different protected areas that protect the same register.' WRONG! If you define two protected areas with overlapping registers, the program will panic with this error message (if you have a kernel area, and a test area, with overlapping register 0 + register 1):
- KERNEL PANIC: REGISTER R0 WRITE VIOLATION: protected in test but trying to write in kernel

Security model:
- Register write isolation ✅
- Register read isolation ✅
- Control-flow integrity ✅ (if you never use NI)
- Memory safety ✅


# CVE Database
## Active (unfixed)
## Inactive (fixed)
### ZERO DAY EXPLOIT (this is novel) - 0001-13-2026 CVE-11:31 PM | 13 February 2026 - CRITICAL SEVERITY - CODE EXECUTION/PRIVILEGE ESCALATION
#### By using CVE 0002-14-2026, a program can use NI pointers to make an unconditional jump (like I0 == I0) to a malicious target.
#### Requirements for this to happen:
##### An unconditional jump with a jump target of type NI must exist somewhere in the code and be accessible (which means it must be executed).
#### Fix:
##### Always use labels, fixed integers pointing to instructions or protected pointers.
### NORMAL EXPLOIT (broken access control is a normal thing) - 0001-14-2026 CVE-11:42 AM | 14 February 2026 - MEDIUM SEVERITY - BROKEN ACCESS CONTROL
#### Any program can modify any register.
#### Requirements for this to happen: None (which is even worse than CVE 0002-13-2026 because it can happen any where at any time)
#### Fix:
##### Adding custom pipes to define areas of protected registers (wasn't that hard to implement).
##### Cons:
###### The registers will not be available/protectable outside that area.
###### You cannot embed multiple protected areas in other protected areas.
##### Pros:
###### Even if a program jumps in there, it can't do anything since the code is already set... unless you set a protected register to the value of an unprotected register (don't do that).
###### Protected registers cannot be accessed in other protected areas that specify the same register... or else it'll give a kernel panic. This means that a malicious program can't just define another protected area and bypass your protected area.
##### Example:
###### ```nano
###### :protectedarea
###### |protect protectedarea R1+R2+R3+R4+R5+R6+R7+R8+R9+R10
###### // R1 and R5 can only be edited here.
###### // You can jump here using the label defined in the first line:
###### // JMP I0 Z protectedarea
###### // protectedarea is the name of it.
###### |end protectedarea
###### ```
### NORMAL EXPLOIT (cryptographic issues are normal) - 0002-14-2026 CVE-03:01 PM | 14 February 2026 - LOW SEVERITY - CRYPTOGRAPHIC ISSUES
#### Any register can be read by any program using SET
#### Fix:
##### I realized that you still can't copy a protected register to another register, therefore you can't read it.
### NORMAL EXPLOIT (broken access control is a normal thing) - 0003-14-2026 CVE-03:21 PM - MEDIUM SEVERITY - PROTECTED REGISTER EXFILTRATION VIA NANO (READ LEAK)
#### Fix:
##### Added checking in the NANO call.
"""


program = """
|protect kernel R0+R1
SET R0 I3
SET R1 I0
:LOOP
NANO R0 R1 R1 I2
JMP R1 != I0 LOOP
|end kernel
"""

# Machine state
labels = {}
registers = [0] * 100 # Since a register can contain any number of bits, you can consider this turing complete even if the number of registers is limited.
ip = 0
lines = [line for line in program.splitlines() if line.strip()]

def panic(msg):
    print("KERNEL PANIC:", msg)
    exit(1)

def val(op):
    global ip

    if op.startswith("I"):
        return int(op[1:])

    elif op.startswith("R"):
        # Determine current area
        current_area = None
        for area_name, (lines_in_area, _) in protected_registers.items():
            if ip in lines_in_area:
                current_area = area_name
                break

        # Check protection
        for area_name, (_, regs) in protected_registers.items():
            if op in regs and area_name != current_area:
                panic(f"REGISTER {op} READ VIOLATION: protected in {area_name} but trying to read in {current_area or 'outside any area'}")

        return registers[int(op[1:])]

def set_target(op, value):
    global ip

    # Find the current area covering this line (if any)
    current_area = None
    for area_name, (lines_in_area, _) in protected_registers.items():
        if ip in lines_in_area:
            current_area = area_name
            break

    # Check all protected registers
    for area_name, (_, regs) in protected_registers.items():
        if op in regs and area_name != current_area:
            panic(f"REGISTER {op} WRITE VIOLATION: protected in {area_name} but trying to write in {current_area or 'outside any area'}")
        if op.startswith("NR"):
            if "R" + str(registers[int(op[2:])]) in regs and area_name != current_area:
                panic(f"REGISTER {op} WRITE VIOLATION: protected in {area_name} but trying to write in {current_area or 'outside any area'}")

    # If allowed, perform the write
    if op.startswith("R"):
        registers[int(op[1:])] = value
    elif op.startswith("NR"):
        registers[registers[int(op[2:])]] = value
    else:
        panic(f"INVALID TARGET {op}")

def resolve_jump_target(op):
    if op.startswith("I"):
        return int(op[1:])
    elif op.startswith("R"):
        return registers[int(op[1:])]
    elif op.startswith("NI"):
        print("!!! WARNING !!!\nTHE VARIABLE TYPE 'NI' IS DANGEROUS IF USED IN UNPROTECTED AREAS, OR PROTECTED AREAS WHERE OUTSIDE INPUT DETERMINES THE VALUE OF THIS REGISTER. I hope you know what you're doing, because this can cause arbitrary code execution.")
        return registers[int(op[2:])]
    else:
        if op in labels:
            return labels[op]
        else:
            panic("INVALID JMP TARGET")

comparisons = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<":  lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
}

# Step 1: Collect labels
while ip < len(lines):
    line = lines[ip].strip()
    parts = line.split()
    if parts[0].startswith(":"):
        labels[parts[0][1:]] = ip + 1
    ip += 1

ip = 0

# Step 2: Detect protected areas
protected_registers = {}
while ip < len(lines):
    line = lines[ip].strip()
    if line.startswith("|protect"):
        parts = line.split()
        area_name = parts[1]
        regs = parts[2].split("+")
        if area_name in protected_registers:
            panic("REDEFINED PROTECTED AREA")
        # collect lines inside this protected area
        protected_lines = []
        index = 1
        while True:
            try:
                if lines[ip + index].startswith(f"|end {area_name}"):
                    break
            except IndexError:
                panic("Protection area without end.")
            protected_lines.append(ip + index)
            index += 1
        protected_registers[area_name] = (protected_lines, regs)
    ip += 1

ip = 0

# Step 3: Execute program
while ip < len(lines):
    line = lines[ip].strip()
    parts = line.split()

    # Ignore labels/comments
    if parts[0].startswith(":") or parts[0].startswith("|"):
        ip += 1
        continue

    # SET
    if parts[0] == "SET":
        _, A, B = parts
        set_target(A, val(B))

    # NANO (NAND)
    elif parts[0] == "NANO":
        _, a, b, c, d = parts
        a_val = val(a)
        b_val = val(b)
        d_val = val(d)
        mask = (1 << d_val) - 1
        result = (~(a_val & b_val)) & mask
        set_target(c, result)

    # JMP
    elif parts[0] == "JMP":
        should_jump = False

        if len(parts) == 5:  # binary comparison
            _, A, op, B, target = parts
            if op not in comparisons:
                panic(f"INVALID CMP OP {op} AT {ip}")
            should_jump = comparisons[op](val(A), val(B))
        elif len(parts) == 4:  # unary zero checks
            _, A, op, target = parts
            a_val = val(A)
            if op == "Z":
                should_jump = (a_val == 0)
            elif op == "NZ":
                should_jump = (a_val != 0)
            else:
                panic(f"INVALID JMP OP {op} AT {ip}")
        else:
            panic(f"INVALID JMP FORMAT AT {ip}")

        if should_jump:
            ip = resolve_jump_target(target)
            continue

    ip += 1

print(registers)

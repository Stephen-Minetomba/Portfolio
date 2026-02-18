program = """
SET R1 I10
JMP :endwhile I0==I0
:while
ADD R1 I-1
:endwhile
JMP :while R1!=I0
"""

labels = {}
ip = 0
for line in program.splitlines():
    line = line.lower()
    if not (line.split(" ")[0].startswith("set") or line.split(" ")[0].startswith("jmp") or line.split(" ")[0].startswith("add") or line.split(" ")[0].startswith("raw") or line.split(" ")[0].startswith(":")):
        continue
    if line.startswith(":"):
        labels[str(line[1:]).lower()] = "i" + str(ip - 1)
    ip += 1

output = []
for line in program.splitlines():
    line = line.lower()
    parts = line.split(" ")
    if line.startswith("raw"):
        output.append("purple " + line[4:])
    elif line.startswith("set"):
        if parts[1].startswith("r"):
            parts[1] = "i" + parts[1][1:]
        elif parts[1].startswith("p"):
            parts[1] = "r" + parts[1][1:]
        else:
            print("[WARNING] Compiler warning: Invalid type used in argument 0 of a set instruction.")
        output.append(f"purple {parts[1]} {parts[2]} i0==i0 0")
    elif line.startswith("add"):
        if parts[1].startswith("r"):
            parts[1] = "i" + parts[1][1:]
        elif parts[1].startswith("p"):
            parts[1] = "r" + parts[1][1:]
        else:
            print("[WARNING] Compiler warning: Invalid type used in argument 0 of an add instruction.")
        output.append(f"purple {parts[1]} {parts[2]} i0==i0 1")
    elif line.startswith("jmp"):
        if parts[1][0].startswith(":"):
            target = labels[str(parts[1][1:])]
        else:
            target = parts[1]
        output.append(f"purple i0 {target} {parts[2]} 0")
print('\n'.join(output))
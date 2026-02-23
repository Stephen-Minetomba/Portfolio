# Program counter address:
## R0
# Instructions:
## setif <register> <register/integer> <condition> <do addition, boolean value? Addition between value 1, value 2, where value 1 gets overwritten> - This implements unconditional jumping, conditional jumping, arithmetic and memory manipulation
# Argument types:
## I - Integer (must specify)
## R - Register (must specify, unless it is the only possible argument type)
## C - Condition (must not specify)
### Format: R<condition>R
### Possible conditions:
#### ==
#### !=
#### >
#### <
#### >=
#### <=
## B - Boolean value (must not specify)

memory = [0] * 100 # 100 bytes of memory

def do_instruction(instruction: str):
    if not instruction.lower().startswith("purple"):
        return
    
    parts = instruction.split(" ")
    if len(parts) != 5:
        print("PANIC: Invalid instruction length")
        return

    # Helper to resolve R/I values
    def resolve(value):
        value = value.strip()
        if value.upper().startswith("I"):
            return int(value[1:])
        elif value.upper().startswith("R"):
            return memory[int(value[1:])]
        else:
            print("PANIC: Invalid R/I value")
            exit(0)

    r1 = resolve(parts[1])
    ri2 = parts[2]
    c3 = parts[3]
    b4 = int(parts[4])

    # Resolve ri2
    ri2 = resolve(ri2)

    # Resolve condition
    cond_ops = [">=", "<=", "==", "!=", ">", "<"]

    for op in cond_ops:
        if op in c3:
            left_raw, right_raw = c3.split(op)

            left = resolve(left_raw)
            right = resolve(right_raw)

            condition_met = (
                (op == "==" and left == right) or
                (op == "!=" and left != right) or
                (op == ">"  and left > right) or
                (op == "<"  and left < right) or
                (op == ">=" and left >= right) or
                (op == "<=" and left <= right)
            )

            if condition_met:
                if b4 == 1:
                    memory[r1] += ri2
                else:
                    memory[r1] = ri2
            break

program = """

purple i1 i8 i0==i0 0
purple i1 i-1 i0==i0 1
purple i2 r1 i0==i0 0
purple i2 i1 i0==i0 1
purple r2 r1 i0==i0 0
purple i0 i0 r1!=i0 0

""".splitlines()
program = [i for i in program if i]

while memory[0] < len(program):
    do_instruction(program[memory[0]])
    memory[0] += 1
print(memory)

# The only rule:
# 1. Never use register 0 unless you're doing jumping or some special programmer vodoo.

# Debugging:
# 1. If you want to overwrite register 0 with integer 1, then do "purple i0 i1 i0==i0 0", not "purple r0 i1 i0==i0 0".

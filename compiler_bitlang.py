output = ""
with open("program.c", "r") as file:
    program = file.readlines()
for line in program:
    processed_line = line.replace("{", "").replace("}", "").replace(" ", "").replace("\n", "").replace(";", "").replace("[", "").replace("]", "")
    if not processed_line or processed_line.startswith("//"):
        continue
    splitter = processed_line.split("(")
    splitter[-1] = splitter[-1].replace(")", "")
    instruction = splitter[0]
    arguments = splitter[-1].split(",")
    for i in range(len(arguments)):
        arguments[i] = int(arguments[i])
    print("Processing...")
    print(arguments)
    print(instruction)
    print("----------")
    if instruction == "while":
        inp2 = arguments[0]
        output += f"{inp2 * '>'}[{inp2 * '<'}"
    if instruction == "cwhile":
        inp2 = arguments[0]
        output += f"{inp2 * '>'}]{inp2 * '<'}"
    if instruction == "if":
        inp2 = arguments[0]
        inp3 = arguments[1]
        output += ">" * inp2
        if inp3 == 1:
            output += "("
        else:
            output += "{"
        output += "<" * inp2
    if instruction == "cif":
        inp2 = arguments[0]
        inp3 = arguments[1]
        output += inp2 * ">"
        if inp3 == 1:
            output += ")"
        else:
            output += "}"
        output += inp2 * "<"
    if instruction == "toggle":
        inp2 = arguments[0]
        output += ">" * inp2 + "T" + "<" * inp2
    if instruction == "print":
        inp2 = arguments[0]
        output += ">" * inp2 + "." + "<" * inp2
    if instruction == "input":
        inp2 = arguments[0]
        output += ">" * inp2 + "," + "<" * inp2
while "<>" in output:
    output = output.replace("<>", "")
print(output.strip())

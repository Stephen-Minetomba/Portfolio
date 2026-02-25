"""
Rules:
- Never have nested 'rpt' or nested 'whl'. Example: rpt 2 rpt 2 inc cell 1, this will give an error.
- Never use cell 0
Notes:
- Raw code will always be better in terms of efficiency. This language is made for convenience.

Documentation:
- whl is for starting a loop, endwhl is for ending a loop. Debug: Make sure you ended a loop. Make sure you also made the 'cell' argument in the endwhl be the same as the one in the whl.
- use raw if you need extremely efficient code or if a feature is missing (unlikely).
- rpt can be used inside a whl (useful in division and multiplication).

Tested Examples:
|> Division (34 divided by 2)
| - rpt 34 inc cell 1
| - whl cell 1
| - rpt 2 dec cell 1
| - inc cell 2
| - endwhl
| - say 1
| - say 2
|> Multiplication (50 times 5)
| - rpt 50 inc cell 1
| - rpt 5 inc cell 2
| - whl cell 1
| - dec cell 1
| - cpy cell 2 into cell 3
| - endwhl cell 1
| - nul cell 2
| - say 3

All possible instructions:
| "say 1" # Says the value of cell 1 as ascii values
| "tog cell 1" # Flips cell 1
| "raw >.<" # Executes raw brainfuck code (note: the pointer should always be at cell 0 after executing an instruction, this is because the python script cannot/doesn't keep track of the cells, which means it must do everything blindly)
| "whl cell 1" # Starts a while cell 1 != 0 loop.
| "endwhl cell 1" # Ends a while loop
| "nul cell 1" # Sets cell 1 to 0 no matter what
| "mov cell 1 into cell 2" # Moves/adds the value of cell 1 to cell 2
| "spt cell 1 into cell 2 and cell 3" # Splits cell 1 into cell 2 and cell 3 (splitting does not mean division by 2. It means copying the same value in two cells)
| "inp cell 1" # Take user input and overwrite cell 1 with the ASCII value of the character the user inputted
| "cpy cell 1 into cell 2" # Copies cell 1 into cell 2 using cell 0 in the back
"""



# Code for calculating the factorial of 5.
code = """
rpt 83 inc cell 1
say 1
rpt 116 inc cell 2
say 2
""".splitlines()

code_temp = []
for line in code:
    if line.startswith("rpt"):
        factor_1 = int(line.split(" ", maxsplit=2)[1])
        factor_2 = line.split(" ", maxsplit=2)[2]
        for i in range(factor_1):
            code_temp.append(factor_2)
    elif line.startswith("cpy"):
        cell_1 = line.split(" ")[2]
        cell_2 = line.split(" ")[5]
        code_temp.append(f"spt cell {cell_1} into cell 0 and cell {cell_2}")
        code_temp.append(f"mov cell 0 into cell {cell_1}")
        code_temp.append("nul cell 0")
    else:
        code_temp.append(line)
code = code_temp
del code_temp # Delete the temporary variable
final_result = []

def resolve_lines(line: str):
    result = []
    if line.startswith("say"):
        characters = [n for part in line[4:].split(",") for n in (range(int(part.split("...")[0]), int(part.split("...")[1]) + 1) if "..." in part else [int(part)])]
        for cell in characters:
            result.append(">" * cell + "." + "<" * cell)
    if line.startswith("sub cell"):
        cell_1 = int(line[9:].split(" ")[0])
        cell_2 = int(line[9:].split(" ")[3])
        result.append(">" * cell_1 + f"[-{'<' * cell_1}{'>' * cell_2}-{'<' * cell_2}{'>' * cell_1}]" + "<" * cell_1)
    if line.startswith("inc cell"):
        cell = int(line[9:])
        result.append(">" * cell + "+" + "<" * cell)
    if line.startswith("dec cell"):
        cell = int(line[9:])
        result.append(">" * cell + "-" + "<" * cell)
    if line.startswith("raw"):
        result.append(line[4:])
    if line.startswith("whl"):
        cell = int(line.split(" ")[2])
        result.append(">[<")
    if line.startswith("endwhl"):
        cell = int(line.split(" ")[2])
        result.append(">]<")
    if line.startswith("nul"):
        cell = int(line.split(" ")[2])
        result.append('>' * cell + "[-]" + '<' * cell)
    if line.startswith("mov"):
        cell_1 = int(line.split(" ")[2])
        cell_2 = int(line.split(" ")[5])
        result.append(f"{cell_1 * '>'}[-{cell_1 * '<'}{cell_2 * '>'}+{cell_2 * '<'}{cell_1 * '>'}]{cell_1 * '<'}")
    if line.startswith("spt"):
        cell_1 = int(line.split(" ")[2])
        cell_2 = int(line.split(" ")[5])
        cell_3 = int(line.split(" ")[8])
        result.append('>' * cell_1 + f"[-{cell_1 * '<'}{cell_2 * '>'}+{cell_2 * '<'}{cell_3 * '>'}+{cell_3 * '<'}{cell_1 * '>'}]{cell_1 * '<'}")
    if line.startswith("inp"):
        cell = int(line.split(" ")[2])
        result.append('>' * cell + "," + '<' * cell)
    return result

for line in code:
    final_result.append(resolve_lines(line))

string = ""
for item in final_result:
    if item:
        string = string + item[0]

# Apply heavy compression and print the output
string = string.strip()
while "<>" in string:
    string = string.replace("<>", "")

bitfuck = False
if bitfuck:
    string = string.replace("+", "T")
    string = string.replace("-", "T")
print(string)

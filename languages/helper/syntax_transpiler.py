import re
# This library is made to make transpiling code easy (without messing with alien-code looking regex expressions).
## Argument format:
### $A<argument index starting at 1, not 0>
## Examples of usages of this library:
### ```python
### table = {
###     "MOVI $A1:I $A2:I": "purple i$A1 i$A2 i0==i0 0 0",
###     "MOV $A1:I $A2:I": "purple i$A1 r$A2 i0==i0 0 0",
###     "PMOV $A1:I $A2:I": "purple r$A1 r$A2 i0==i0 0 0",
###     "JMPI $A1:I $A2:T": "purple i0 i$A1 $A2 0 0",
###     "PJMP $A1:I $A2:T": "purple i0 r$A1 $A2 0 0",
###     "ADDI $A1:I $A2:I": "purple i$A1 i$A2 i0==i0 1 0",
###     "ADD $A1:I $A2:I": "purple i$A1 r$A2 i0==i0 1 0",
###     "SUBI $A1:I $A2:I": "purple i$A1 i$A2 i0==i0 1 1",
###     "SUB $A1:I $A2:I": "purple i$A1 r$A2 i0==i0 1 1"
### }
### code = """
### MOVI 1 5
### MOVI 2 5
### JMPI 5 r3>=r2
### ADD 4 1
### ADDI 3 1
### JMPI 2 r3<r2
### """
### code = [i for i in code.splitlines() if i]
### print('\n'.join(transpile(table, code)))
### ```
## Also, a really cool feature is that you can make multiple instructions per instruction, not just one. Just separate them using a semicolon (no spaces afterwards btw)

# Unfixed bugs:
## - Overlapping placeholders (example: if there's $A1:I and $A10:I)

import re

type_map = {
    "T": ".+",
    "S": "[a-zA-Z]+",
    "L": "[a-z]+",
    "U": "[A-Z]+",
    "I": r"-?\d+",
    "C": r"[\x20-\x7E]",
    "J": r"\d"
}

def transpile(table: dict[str, str], code: list[str]) -> list[str]:
    """
    Transpile code lines based on a pattern table.
    Supports typed placeholders ($A1:T, $A2:I, etc.), indexing ($AI1),
    and multiple instructions per output line separated by ';'.
    """
    compiled_table = []
    for pattern, output_template in table.items():
        regex_pattern = pattern
        for match in re.findall(r"\$A(\d+)(?::([TSLUICJ]))?", pattern):
            arg_num, arg_type = match
            arg_type = arg_type or "T"
            regex_group = f"({type_map[arg_type]})"
            regex_pattern = regex_pattern.replace(f"$A{arg_num}" + (f":{arg_type}" if arg_type else ""), regex_group)
        compiled_table.append((re.compile(f"^{regex_pattern}$"), output_template))

    result = []

    for i, line in enumerate(code, start=1):
        matched = False
        for regex, template in compiled_table:
            m = regex.match(line)
            if m:
                matched = True
                output_line = template
                for idx, val in enumerate(m.groups(), start=1):
                    output_line = output_line.replace(f"$A{idx}", val)
                    output_line = output_line.replace(f"$AI{idx}", str(i))

                result.extend(output_line.split(";"))
                break
        if not matched:
            print("not matched")
            result.append(line)

    return result
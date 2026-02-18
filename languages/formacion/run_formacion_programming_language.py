##################################################
# Define program
program = """
DEFINE name {
    CREATE S3;
    SAY-VALUE S1;
    NEW-LINE;
    APPEND S3 5;
}
CREATE S1;
CREATE S2;
APPEND S1 10;
APPEND S2 10;
IF S1 == S2 CALL name;
SAY-VALUE S3;
"""

##################################################
# Format program (keep lines separate for DEFINE)
program_lines = [
    line.strip().rstrip(";")  # remove trailing semicolons
    for line in program.strip().split("\n")
    if line.strip()
]

##################################################
# Interpreter
stacks = {}        # Dictionary of named stacks
functions = {}     # Dictionary of named functions

trace_mode = True
def debug(message: str):
    if trace_mode:
        print(f"[DEBUG] {message}")

def run_block(block):
    debug("Running block...")
    debug("Setting program counter to zero...")
    i = 0
    debug("Looping over the program...")
    while i < len(block):
        debug("Extracting the line from the program...")
        stmt = block[i]
        debug("Testing if the line exists...")
        if not stmt:
            debug("The line is empty. Incrementing program counter...")
            i += 1
            debug("Continuing to the next line...")
            continue
        debug("Extracting arguments...")
        parts = stmt.split()
        debug("Extracting instruction name...")
        cmd = parts[0].upper()

        debug("Testing for all the different functions...")
        if cmd == "CREATE":
            debug("Running the create function...")
            debug("CREATE <stack>; - Creates a new stack (tip: you can use CREATE on an existing stack to reset it)")
            debug("Extracting stack name...")
            name = parts[1]
            debug("Creating stack...")
            stacks[name] = []
        
        elif cmd == "DELETE":
            debug("Running the delete function...")
            debug("DELETE <stack>; - Deletes the stack from RAM")
            debug("Extracting stack name...")
            name = parts[1]
            debug("Deleting stack...")
            del stacks[name]

        elif cmd == "APPEND":
            debug("Running the append function...")
            debug("APPEND <stack> <number>; - Appends that value to the stack")
            debug("Extracting stack name...")
            name = parts[1]
            debug("Extracting value...")
            value = int(parts[2])
            debug("Appending value to the stack...")
            stacks[name].append(value)

        elif cmd == "REMOVE":
            debug("Running the remove function...")
            debug("REMOVE <stack>; - Removes the last value in the stack")
            debug("Extracting name...")
            name = parts[1]
            debug("Testing if the stack exists...")
            if stacks[name]:
                debug("The stack exists!")
                debug("Popping last value from the stack...")
                stacks[name].pop()

        elif cmd == "DUPLICATE":
            debug("Running the duplicate function...")
            debug("DUPLICATE <stack>; - Duplicates the last value in the stack")
            debug("Extracting name...")
            name = parts[1]
            debug("Testing if the stack exists...")
            if stacks[name]:
                debug("The stack exists!")
                debug("Appending the last value of the stack to the same stack (which duplicates the last value)...")
                stacks[name].append(stacks[name][-1])

        elif cmd == "SWAP":
            debug("Running the swap function...")
            debug("SWAP <stack>; - Swaps the top two values in the stack")
            debug("Extracting stack name...")
            name = parts[1]
            debug("Testing if the stack has at least two values...")
            if len(stacks[name]) >= 2:
                debug("The stack has at least two values!")
                debug("Swapping the top two values of the stack...")
                stacks[name][-1], stacks[name][-2] = stacks[name][-2], stacks[name][-1]

        elif cmd == "ADD":
            debug("Running the add function...")
            debug("ADD <stack>; - Pops top two values and pushes their sum")
            debug("Extracting stack name...")
            name = parts[1]
            debug("Testing if the stack has at least two values...")
            if len(stacks[name]) >= 2:
                debug("The stack has at least two values!")
                debug("Popping top value...")
                b = stacks[name].pop()
                debug("Popping second value...")
                a = stacks[name].pop()
                debug("Adding values together...")
                stacks[name].append(a + b)

        elif cmd == "SUBTRACT":
            debug("Running the subtract function...")
            debug("SUBTRACT <stack>; - Pops top two values and pushes their difference")
            debug("Extracting stack name...")
            name = parts[1]
            debug("Testing if the stack has at least two values...")
            if len(stacks[name]) >= 2:
                debug("The stack has at least two values!")
                debug("Popping top value...")
                b = stacks[name].pop()
                debug("Popping second value...")
                a = stacks[name].pop()
                debug("Subtracting values...")
                stacks[name].append(a - b)

        elif cmd == "MULTIPLY":
            debug("Running the multiply function...")
            debug("MULTIPLY <stack>; - Pops top two values and pushes their product")
            debug("Extracting stack name...")
            name = parts[1]
            debug("Testing if the stack has at least two values...")
            if len(stacks[name]) >= 2:
                debug("The stack has at least two values!")
                debug("Popping top value...")
                b = stacks[name].pop()
                debug("Popping second value...")
                a = stacks[name].pop()
                debug("Multiplying values...")
                stacks[name].append(a * b)

        elif cmd == "DIVIDE":
            debug("Running the divide function...")
            debug("DIVIDE <stack>; - Pops top two values and pushes integer division result")
            debug("Extracting stack name...")
            name = parts[1]
            debug("Testing if the stack has at least two values...")
            if len(stacks[name]) >= 2:
                debug("The stack has at least two values!")
                debug("Popping top value...")
                b = stacks[name].pop()
                debug("Popping second value...")
                a = stacks[name].pop()
                debug("Testing if divisor is zero...")
                debug("Performing safe division...")
                stacks[name].append(a // b if b != 0 else 0)

        elif cmd == "SAY-VALUE":
            debug("Running the say-value function...")
            debug("SAY-VALUE <stack>; - Pops and prints the top value")
            debug("Extracting stack name...")
            name = parts[1]
            debug("Testing if the stack exists and is not empty...")
            if stacks[name]:
                debug("The stack exists and is not empty!")
                debug("Popping value and printing it...")
                if trace_mode:
                    print(stacks[name].pop())
                else:
                    print(stacks[name].pop(), end="")
        
        elif cmd == "SAY-ASCII":
            debug("Running the say-ascii function...")
            debug("SAY-ASCII <stack>; - Pops and prints ASCII character of top value")
            debug("Extracting stack name...")
            name = parts[1]
            debug("Testing if the stack exists and is not empty...")
            if stacks[name]:
                debug("The stack exists and is not empty!")
                debug("Popping value and converting to ASCII character...")
                if trace_mode:
                    print(chr(stacks[name].pop()))
                else:
                    print(chr(stacks[name].pop()), end="")

        elif cmd == "NEW-LINE":
            debug("Running the new-line function...")
            debug("NEW-LINE; - Prints a newline character")
            debug("Printing newline...")
            if trace_mode:
                debug("Excluded newline (due to trace mode)")
            else:
                print("\n", end="")

        elif cmd == "COPY":
            debug("Running the copy function...")
            debug("COPY <src> <dst>; - Copies top value from source stack to destination stack")
            debug("Extracting source stack name...")
            src = parts[1]
            debug("Extracting destination stack name...")
            dst = parts[2]
            debug("Testing if the source stack exists and is not empty...")
            if stacks[src]:
                debug("The source stack exists and is not empty!")
                debug("Copying top value to destination stack...")
                stacks[dst].append(stacks[src][-1])

        elif cmd == "DEFINE":
            debug("Running the define function...")
            debug("DEFINE <name> { ... } - Defines a new function")
            debug("""
            # The functions must be formatted like this:
            # DEFINE name {
            #   APPEND S1 10;
            #   SAY S1;
            # }
            # Do not forget:
            # 1. Intendation
            # 2. Semicolons (don't add one on the final bracket)
            # 3. Putting a bracket on the same line as the DEFINE, and putting a bracket after the last instruction.
            # 4. The fact that all stacks are global.
            # 5. The semicolons and brackets are only there to help the indentation, they do not mean you can put everything into a single line.
            """)
            debug("Extracting function name...")
            fname = parts[1]
            debug("Creating function block container...")
            func_block = []
            debug("Incrementing program counter to enter function body...")
            i += 1
            debug("Initializing brace counter...")
            brace_count = 1
            debug("Looping through lines to capture function body...")
            while i < len(block):
                debug("Extracting line inside function body...")
                line = block[i]
                debug("Testing for opening brace...")
                if "{" in line: brace_count += 1
                debug("Testing for closing brace...")
                if "}" in line: brace_count -= 1
                debug("Testing if brace counter reached zero...")
                if brace_count == 0:
                    debug("End of function definition reached!")
                    break
                debug("Appending line to function block...")
                func_block.append(line)
                debug("Incrementing program counter inside function definition...")
                i += 1
            debug("Storing function in functions dictionary...")
            functions[fname] = func_block

        elif cmd == "CALL":
            debug("Running the call function...")
            debug("CALL <name>; - Calls a defined function")
            debug("Extracting function name...")
            fname = parts[1]
            debug("Testing if function exists...")
            if fname in functions:
                debug("Function exists! Running function block...")
                run_block(functions[fname])

        elif cmd == "IF":
            debug("Running the if function...")
            debug("IF <stack1> <op> <stack2> CALL <function>; - Conditional function call")
            debug("Extracting first stack name...")
            stack1 = parts[1]
            debug("Extracting operator...")
            op = parts[2]
            debug("Extracting second stack name...")
            stack2 = parts[3]

            debug("Testing for CALL keyword...")
            if len(parts) >= 5 and parts[4].upper() == "CALL":
                debug("CALL keyword found!")
                fname = parts[5]
                debug("Testing if function exists...")
                if fname not in functions:
                    debug("Function does not exist. Skipping...")
                    i += 1
                    continue
            else:
                debug("No CALL keyword found.")
                fname = None

            debug("Testing if both stacks exist and are not empty...")
            if not stacks.get(stack1) or not stacks.get(stack2):
                debug("One or both stacks do not exist or are empty. Skipping...")
                i += 1
                continue

            debug("Extracting top values from both stacks...")
            top1 = stacks[stack1][-1]
            top2 = stacks[stack2][-1]

            debug("Evaluating condition...")
            condition = False
            if op == "==": condition = top1 == top2
            if op == "!=": condition = top1 != top2
            if op == ">": condition = top1 > top2
            if op == "<": condition = top1 < top2
            if op == ">=": condition = top1 >= top2
            if op == "<=": condition = top1 <= top2

            debug("Testing if condition is true and function should be called...")
            if condition and fname:
                debug("Condition is true! Calling function...")
                run_block(functions[fname])

        i += 1

##################################################
# Run the program
run_block(program_lines)

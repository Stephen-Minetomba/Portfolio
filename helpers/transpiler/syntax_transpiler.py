import re; type_map = {
    "T": ".+?",
    "S": "[a-zA-Z]+",
    "L": "[a-z]+",
    "U": "[A-Z]+",
    "I": r"-?\d+",
    "C": r"[\x20-\x7E]",
    "J": r"\d"
}
debug = False
def d(text: str):
    if debug:
        print(f"[DEBUG] {text}")
def transpile(table: dict[str, str], code: list[str]) -> list[str]:
    """
    Transpile code lines based on a pattern table.
    Supports typed placeholders ($A1:T, $A2:I, etc.), indexing ($AI1),
    and multiple instructions per output line separated by ';'.
    """
    d("Setting up compiled table...")
    compiled_table = []
    d("Starting loop...")
    for pattern, output_template in table.items():
        d("Setting regex pattern...")
        regex_pattern = pattern
        d(f"Regex pattern before: {regex_pattern}")
        # Escape brackets BEFORE anything (they're literal chars in pattern)
        regex_pattern = regex_pattern.replace("[", r"\[").replace("]", r"\]")
        d(f"Regex pattern after: {regex_pattern}")
        # Find placeholders and replace with unique markers first
        d("Finding placeholders...")
        placeholders = []
        d("Looping...")
        for match in re.findall(r"\$A(\d+)(?::([TSLUICJ]))?", regex_pattern):
            d(f"Match = {match}")
            arg_num, arg_type = match
            arg_type = arg_type or "T"
            placeholder = f"\x00GROUP{len(placeholders)}\x00"
            placeholders.append((placeholder, f"({type_map[arg_type]})"))
            old = f"$A{arg_num}" + (f":{arg_type}" if arg_type else "")
            d(f"Regex pattern before: {regex_pattern}")
            regex_pattern = regex_pattern.replace(old, placeholder, 1)
            d(f"Regex pattern after: {regex_pattern}")
        # Now escape special chars (no groups to worry about)
        d("Escaping special chars...")
        regex_pattern = re.sub(r"([.^$*+?{}|])", r"\\\1", regex_pattern)
        d(f"Regex after escape: {regex_pattern}")
        # Replace markers with actual groups
        d("Replacing markers with groups...")
        for placeholder, group in placeholders:
            regex_pattern = regex_pattern.replace(placeholder, group)
        d(f"Final regex: {regex_pattern}")
        final_pattern = f"^{regex_pattern}$"
        d(f"Final pattern string: {repr(final_pattern)}")
        compiled_table.append((re.compile(final_pattern), output_template))
        d(f"Compiled pattern: {compiled_table[-1][0]}")

    result = []

    for i, line in enumerate(code, start=1):
        d(f"Processing line: {repr(line)}")
        matched = False
        for j, (regex, template) in enumerate(compiled_table):
            d(f"Trying pattern {j}: {regex}")
            m = regex.match(line)
            d(f"Match result: {m}")
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
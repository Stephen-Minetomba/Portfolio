macros = {
	"LSH": ["DUP", "+"], # BUILT-IN MACRO
	"NOT": ["0", "NOR"],
	"NEG": ["NOT", "1", "+"],
	"SUB": ["NEG", "+"],
	"JG": ["SWAP", "JL"]
}
documentation = {
	"PC": {
		"opcode": "10",
		"arguments": "...",
		"description": "Returns the current program counter value.",
		"uses": "In macros requiring dynamic jump targets like 'CALL' or 'RETURN'."
	},
	"@": {
		"opcode": "6",
		"arguments": "... | address",
		"description": "(address popped) Pushes the 64-bit value located at that memory address into the stack."
	},
	"!": {
		"opcode": "7",
		"arguments": "... | address | value",
		"description": "(address, value popped) Stores that 64-bit value in the memory location at the specified address."
	},
	"+": {
		"opcode": "1",
		"arguments": "... | value 1 | value 2",
		"description": "(both values popped) Pushes the result of value 2 + value 1."
	},
	"LSH": {
		"opcode": "2",
		"arguments": "... | value",
		"description": "(value popped) Shifts that value by one, and pushes the result."
	},
	"NOR": {
		"opcode": "3",
		"arguments": "... | value | value",
		"description": "(both values popped) Pushes the result of a bitwise NOR operation."
	},
	"NUM": {
		"opcode": "4",
		"arguments": "...",
		"description": "Pushes that value on the stack."
	},
	"JL": {
		"opcode": "5",
		"arguments": "... | address or label name (label name resolving is specified by using a dot as a prefix) | value 1 | value 2",
		"description": "(address, both values popped) If value 2 is less than value 1, it sets the program counter to the specified address."
	},
	"DUP": {
		"opcode": "8",
		"arguments": "... | value",
		"description": "(value not popped) Pushes that value on the stack (basically duplicating it)."
	},
	"SWAP": {
		"opcode": "9",
		"arguments": "... | value 1 | value 2",
		"description": "(both values popped) Pushes value 2, followed by value 1 (basically swapping them together)."
	},
	"DROP": {
		"opcode": "2",
		"arguments": "... | value",
		"description": "(value popped)"
	},
	"LABEL:": {
		"opcode": "NONE (well, technically interacts with opcode 4 when you query its location)",
		"arguments": "...",
		"description": "(nothing) Takes note of the address of the current label, address to be queried with the dot (this is done in the first pass, so that you can forward-jump. no need to say thank you ;D)."
	},
	".LABEL": {
		"opcode": "4",
		"arguments": "...",
		"description": "(nothing) Pushes the location of that label into the stack."
	}
}
tokens = ["5", "5", "+"]
def assemble(ntokens: list[str], macros: dict[str, list[str]]) -> list[int]:
	def extend(tokens_, seen=None) -> list[str]:
		if seen is None:
			seen = set()
		result = []
		for token in tokens_:
			if token in macros:
				if token in seen:
					raise RecursionError(f"[RECURSION ERROR] Recursive macro: {token}")
				result.extend(extend(macros[token], seen | {token}))
			else:
				result.append(token)
		return result
	output = []
	tokens = extend(ntokens)

	labels = {}
	instructions = []
	current_address = 0
	i = 0
	while i < len(tokens):
		token = tokens[i]
		if token.endswith(":"):
			label_name = token[:-1]
			if label_name in labels:
				print(f"[DUPLICATE LABEL ERROR] Two labels with the same name found: {label_name}")
				exit(1)
			labels[label_name] = current_address
			i += 1
			continue
		if token.startswith("."):
			instructions.append(('label', token[1:]))
		else:
			instructions.append(token)
		current_address += 1
		i += 1
	for token in instructions:
		if isinstance(token, tuple):
			if token[0] == "label":
				label_name = token[1]
				if label_name not in labels:
					print(f"[LABEL NOT FOUND ERROR] Label not found: {label_name}")
					exit(1)
				output.append(4)
				output.append(labels[label_name])
		elif token == "@":
			output.append(6)
		elif token == "!":
			output.append(7)
		elif token == "+":
			output.append(1)
		elif token == "NOR":
			output.append(3)
		elif token == "JL":
			output.append(5)
		elif token == "DUP":
			output.append(8)
		elif token == "SWAP":
			output.append(9)
		elif token == "DROP":
			output.append(2)
		elif token == "PC":
			output.append(10)
		else:
			try:
				output.append(4)
				output.append(int(token))
			except ValueError:
				output.pop(-1)
				print(f"[SYNTAX ERROR] Invalid instruction: {token}")
				exit(1)
	return output
def doc(token: str):
	try:
		for key, value in documentation[token].items():
			print(f"{key}: {value}")
	except KeyError:
		print(f"[SYNTAX ERROR] Invalid instruction: {token}")
print("{" + ', '.join([str(i) for i in assemble(tokens, macros)]) + "}")
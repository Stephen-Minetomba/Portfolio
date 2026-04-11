import itertools
import re

# -------------------------------
# Token types
# -------------------------------
TOKEN_SPECIFICATION = [
    ("COMMENT", r"//.*"),
    ("NUMBER", r"0x[0-9A-Fa-f]+|\d+"),
    ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP", r"->|[\+\-\*/%=&|!<>^]+"),
    ("DOT", r"\."),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("LBRACK", r"\["),
    ("RBRACK", r"\]"),
    ("SEMICOL", r";"),
    ("COMMA", r","),
    ("WS", r"\s+"),
    ("UNKNOWN", r"."),
]

TYPES = {"i64", "i32", "i16", "i8", "u64", "u32", "u16", "u", "void", "int"}
ARRAY_TYPES = {t + "[]" for t in TYPES}
ALL_TYPES = TYPES.union(ARRAY_TYPES)
KEYWORDS = {"while", "if", "else", "goto", "return", "asm", "efi_setup", "struct"}


# -------------------------------
# Tokenizer
# -------------------------------
def tokenize(code):
    tok_regex = "|".join(
        f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION
    )
    get_token = re.compile(tok_regex).match
    pos = 0
    tokens = []
    while pos < len(code):
        match = get_token(code, pos)
        if not match:
            raise SyntaxError(f"Unexpected character: {code[pos]}")
        kind = match.lastgroup
        value = match.group(kind)
        start = pos
        end = match.end()
        if kind == "WS" or kind == "COMMENT":
            pass
        elif kind == "ID":
            if value in ALL_TYPES:
                tokens.append(("TYPE", value, start, end))
            elif value in KEYWORDS:
                tokens.append(("KEYWORD", value, start, end))
            else:
                tokens.append(("ID", value, start, end))
        elif kind == "UNKNOWN":
            tokens.append(("UNKNOWN", value, start, end))
        else:
            tokens.append((kind, value, start, end))
        pos = match.end()
    return tokens


# -------------------------------
# Parser for expressions and statements
# -------------------------------
class Parser:
    def __init__(self, tokens, code, structs=None, variables=None):
        self.tokens = tokens
        self.code = code
        self.pos = 0
        self.label_counter = itertools.count()
        self.variables = variables if variables is not None else {}  # Globals
        self.locals = {}  # Current function locals
        self.structs = structs if structs is not None else {}
        self.prefix = ""

    def peek(self, n=0):
        if self.pos + n < len(self.tokens):
            return self.tokens[self.pos + n]
        return None

    def consume(self, expected_kind=None, expected_value=None):
        tok = self.tokens[self.pos]
        if expected_kind and tok[0] != expected_kind:
            raise SyntaxError(
                f"Expected {expected_kind}, got {tok[0]} at {tok[2]} (value: {tok[1]})"
            )
        if expected_value and tok[1] != expected_value:
            raise SyntaxError(f"Expected {expected_value}, got {tok[1]} at {tok[2]}")
        self.pos += 1
        return tok

    def parse_expression(self):
        return self.parse_binop(0)

    PRECEDENCE = {
        "||": 1,
        "&&": 2,
        "|": 3,
        "^": 4,
        "&": 5,
        "==": 6,
        "!=": 6,
        "<": 7,
        "<=": 7,
        ">": 7,
        ">=": 7,
        "<<": 8,
        ">>": 8,
        "+": 9,
        "-": 9,
        "*": 10,
        "/": 10,
        "%": 10,
    }

    def parse_binop(self, min_prec):
        node = self.parse_primary()
        while True:
            tok = self.peek()
            if (
                tok
                and tok[0] == "OP"
                and tok[1] in self.PRECEDENCE
                and self.PRECEDENCE[tok[1]] >= min_prec
            ):
                op = tok[1]
                self.consume()
                rhs = self.parse_binop(self.PRECEDENCE[op] + 1)
                node = ("binop", op, node, rhs)
            else:
                break
        return node

    def get_variable(self, name):
        if name in self.locals:
            return self.locals[name]
        return self.variables.get(name)

    def parse_primary(self):
        tok = self.peek()
        if not tok:
            raise SyntaxError("Unexpected end of tokens")

        # sizeof support
        if tok[0] == "ID" and tok[1] == "sizeof":
            self.consume()
            has_paren = False
            if self.peek() and self.peek()[0] == "LPAREN":
                self.consume()
                has_paren = True

            name = self.consume()[1]
            if has_paren:
                self.consume("RPAREN")

            v = self.get_variable(name)
            if v:
                bits = v["bits"]
                size = v.get("size", 1)
                return ("number", (bits // 8) * size)
            elif name in self.structs:
                return ("number", self.structs[name]["size_bytes"])
            return ("number", 8)

        # Cast support: (type) expr
        if tok[0] == "LPAREN":
            # Lookahead for cast
            p1 = self.peek(1)
            if p1 and (p1[0] == "TYPE" or p1[1] == "struct"):
                self.consume()  # (
                if self.peek()[1] == "struct":
                    self.consume()
                typ = self.consume()[1]
                while self.peek() and self.peek()[1] == "*":
                    typ += self.consume()[1]
                self.consume("RPAREN")
                expr = self.parse_primary()
                return ("cast", typ, expr)

        if tok[0] == "OP" and tok[1] == "*":
            self.consume()
            return ("deref", self.parse_primary())
        elif tok[0] == "OP" and tok[1] == "&":
            self.consume()
            return ("addr", self.parse_primary())
        elif tok[0] == "OP" and tok[1] == "-":
            self.consume()
            return ("neg", self.parse_primary())

        if tok[0] == "NUMBER":
            val_str = self.consume()[1]
            node = ("number", int(val_str, 0))
        elif tok[0] == "ID" or tok[0] == "TYPE":
            name = self.consume()[1]
            node = ("var", name)
        elif tok[0] == "LPAREN":
            self.consume()
            node = self.parse_expression()
            self.consume("RPAREN")
        else:
            raise SyntaxError(f"Unexpected token {tok}")

        while True:
            nt = self.peek()
            if not nt:
                break
            if nt[0] == "LPAREN":
                self.consume()
                args = []
                while self.peek() and self.peek()[0] != "RPAREN":
                    args.append(self.parse_expression())
                    if self.peek() and self.peek()[0] == "COMMA":
                        self.consume()
                self.consume("RPAREN")
                node = ("call", node[1] if node[0] == "var" else node, args)
            elif nt[0] == "LBRACK":
                self.consume()
                idx = self.parse_expression()
                self.consume("RBRACK")
                node = ("array", node[1] if node[0] == "var" else node, idx)
            elif nt[0] == "DOT":
                self.consume()
                member = self.consume("ID")[1]
                node = ("member", node, member)
            elif nt[0] == "OP" and nt[1] == "->":
                self.consume()
                member = self.consume("ID")[1]
                node = ("arrow", node, member)
            else:
                break
        return node

    def parse_statements(self, end_tokens={"RBRACE"}):
        stmts = []
        while self.pos < len(self.tokens) and self.peek()[0] not in end_tokens:
            tok = self.peek()
            if tok[0] == "TYPE":
                stmts.append(self.parse_var_decl())
            elif tok[0] == "KEYWORD":
                if tok[1] == "struct":
                    if self.peek(2) and self.peek(2)[0] == "LBRACE":
                        # Skip struct def inside block
                        self.parse_struct_def()
                    else:
                        stmts.append(self.parse_var_decl())
                elif tok[1] == "return":
                    stmts.append(self.parse_return())
                elif tok[1] == "goto":
                    stmts.append(self.parse_goto())
                elif tok[1] == "asm":
                    stmts.append(self.parse_asm())
                elif tok[1] in {"while", "if"}:
                    stmts.append(self.parse_control())
                else:
                    self.consume()
            elif tok[0] == "ID":
                stmts.append(self.parse_assignment_or_call())
            elif tok[0] == "OP" and tok[1] == "*":
                # Pointer assignment *p = val
                self.consume()
                ptr_expr = self.parse_primary()
                self.consume("OP", "=")
                val_expr = self.parse_expression()
                self.consume("SEMICOL")
                stmts.append(("ptr_assign", ptr_expr, val_expr))
            else:
                self.consume()
        return stmts

    def parse_var_decl(self):
        is_struct_type = False
        if self.peek()[1] == "struct":
            self.consume()
            is_struct_type = True

        typ = self.consume()[1]
        while self.peek() and self.peek()[1] == "*":
            self.consume()
            typ += "*"

        name = self.consume("ID")[1]
        size = 1
        is_array = False
        if self.peek() and self.peek()[0] == "LBRACK":
            self.consume()
            size = int(self.consume("NUMBER")[1], 0)
            self.consume("RBRACK")
            is_array = True

        is_ptr = "*" in typ
        is_struct = is_struct_type and not is_ptr
        struct_name = typ.replace("*", "") if is_struct_type else None

        bits = 64
        if not is_struct_type:
            if is_ptr:
                bits = 64
            elif "64" in typ or typ == "u":
                bits = 64
            else:
                bits = int("".join(filter(str.isdigit, typ)) or 64)
        else:
            if is_ptr:
                bits = 64
            else:
                if struct_name not in self.structs:
                    raise SyntaxError(f"Unknown struct {struct_name}")
                bits = self.structs[struct_name]["size_bits"]

        mangled = self.prefix + name
        vinfo = {
            "type": typ,
            "bits": bits,
            "array": is_array,
            "is_struct": is_struct,
            "struct_name": struct_name,
            "size": size,
            "mangled": mangled,
        }
        if self.prefix:
            self.locals[name] = vinfo
        else:
            self.variables[name] = vinfo

        init_expr = None
        if self.peek() and self.peek()[1] == "=":
            self.consume()
            init_expr = self.parse_expression()

        if self.peek() and self.peek()[0] == "SEMICOL":
            self.consume()
        return ("var_decl", mangled, size, is_array, typ, init_expr, is_struct)

    def parse_assignment_or_call(self):
        # Lookahead for complex assignment
        curr = self.pos
        try:
            expr = self.parse_primary()
            if self.peek() and self.peek()[1] == "=":
                self.consume()
                val = self.parse_expression()
                self.consume("SEMICOL")
                if expr[0] in {"member", "arrow", "deref"}:
                    return ("member_assign", expr, val)
                elif expr[0] == "var":
                    return ("assign", expr[1], "=", val)
                elif expr[0] == "array":
                    return ("array_assign", expr[1], expr[2], val)
            elif expr[0] == "call":
                if self.peek() and self.peek()[0] == "SEMICOL":
                    self.consume()
                return ("call_stmt", expr[1], expr[2])
        except:
            pass
        self.pos = curr

        # Fallback to simple assign
        name = self.consume()[1]
        op = self.consume("OP")[1]
        val = self.parse_expression()
        self.consume("SEMICOL")
        return ("assign", name, op, val)

    def parse_struct_def(self):
        self.consume("KEYWORD", "struct")
        name = self.consume("ID")[1]
        self.consume("LBRACE")
        members = []
        offset = 0
        while self.peek() and self.peek()[0] != "RBRACE":
            m_type_prefix = ""
            if self.peek()[1] == "struct":
                m_type_prefix = self.consume()[1] + " "

            m_type = m_type_prefix + self.consume()[1]
            while self.peek() and self.peek()[1] == "*":
                self.consume()
                m_type += "*"
            m_name = self.consume("ID")[1]
            bits = 64
            if "*" in m_type:
                bits = 64
            elif "64" in m_type or m_type == "u":
                bits = 64
            else:
                bits = int("".join(filter(str.isdigit, m_type)) or 64)
            members.append(
                {"name": m_name, "type": m_type, "bits": bits, "offset": offset}
            )
            offset += bits // 8
            if self.peek() and self.peek()[0] == "SEMICOL":
                self.consume()
        self.consume("RBRACE")
        if self.peek() and self.peek()[0] == "SEMICOL":
            self.consume()
        self.structs[name] = {
            "members": {m["name"]: m for m in members},
            "size_bytes": offset,
            "size_bits": offset * 8,
        }
        return ("struct_def", name, members)

    def parse_return(self):
        self.consume()
        expr = None
        if self.peek() and self.peek()[0] != "SEMICOL":
            expr = self.parse_expression()
        if self.peek() and self.peek()[0] == "SEMICOL":
            self.consume()
        return ("return", expr)

    def parse_goto(self):
        self.consume()
        name = self.consume("ID")[1]
        if self.peek() and self.peek()[0] == "SEMICOL":
            self.consume()
        return ("goto", name)

    def parse_asm(self):
        self.consume()
        brace = self.consume("LBRACE")
        start = brace[3]
        count = 1
        while self.pos < len(self.tokens) and count > 0:
            t = self.consume()
            if t[0] == "LBRACE":
                count += 1
            elif t[0] == "RBRACE":
                count -= 1
        return ("asm", self.code[start : self.tokens[self.pos - 1][2]].strip())

    def parse_control(self):
        kind = self.consume()[1]
        self.consume("LPAREN")
        cond = self.parse_expression()
        self.consume("RPAREN")
        self.consume("LBRACE")
        body = self.parse_statements()
        self.consume("RBRACE")
        else_body = None
        if kind == "if" and self.peek() and self.peek()[1] == "else":
            self.consume()
            self.consume("LBRACE")
            else_body = self.parse_statements()
            self.consume("RBRACE")
        return (kind, cond, body, else_body)


# -------------------------------
# Transpiler
# -------------------------------
class X86Transpiler:
    def __init__(self, parser, function_signatures):
        self.parser = parser
        self.function_signatures = function_signatures
        self.asm = []
        self.indent = "    "

    def get_expr_info(self, expr):
        if expr[0] == "var":
            v = self.parser.get_variable(expr[1])
            if not v:
                return 64, False, None
            return v["bits"], v["is_struct"], v["struct_name"]
        elif expr[0] == "array":
            v = self.parser.get_variable(expr[1])
            if not v:
                return 64, False, None
            return v["bits"], v["is_struct"], v["struct_name"]
        elif expr[0] == "deref":
            b, s, sn = self.get_expr_info(expr[1])
            return 64, True, sn
        elif expr[0] in {"member", "arrow"}:
            obj, mem = expr[1], expr[2]
            b, s, sn = self.get_expr_info(obj)
            if not sn:
                return 64, False, None
            m = self.parser.structs[sn]["members"][mem]
            is_s = "struct" in m["type"] and "*" not in m["type"]
            sn2 = (
                m["type"].replace("struct ", "").replace("*", "")
                if "struct" in m["type"]
                else None
            )
            return m["bits"], is_s, sn2
        elif expr[0] == "cast":
            return self.get_expr_info(expr[2])
        return 64, False, None

    def expr_to_asm(self, expr, want_addr=False):
        if expr[0] == "number":
            self.asm.append(f"{self.indent}mov rax, {expr[1]}")
        elif expr[0] == "var":
            v = self.parser.get_variable(expr[1])
            mname = v["mangled"] if v else expr[1]
            if want_addr:
                self.asm.append(f"{self.indent}lea rax, [{mname}]")
            else:
                if not v:
                    self.asm.append(f"{self.indent}mov rax, [{mname}]")
                    return
                if v["is_struct"]:
                    self.asm.append(f"{self.indent}lea rax, [{mname}]")
                else:
                    bits = v["bits"]
                    reg = {64: "rax", 32: "eax", 16: "ax", 8: "al"}[bits]
                    if bits >= 32:
                        self.asm.append(f"{self.indent}mov {reg}, [{mname}]")
                    else:
                        self.asm.append(
                            f"{self.indent}movzx rax, { {16: 'word', 8: 'byte'}[bits] } [{mname}]"
                        )
        elif expr[0] == "addr":
            self.expr_to_asm(expr[1], True)
        elif expr[0] == "deref":
            self.expr_to_asm(expr[1])
            if not want_addr:
                self.asm.append(f"{self.indent}mov rax, [rax]")
        elif expr[0] == "cast":
            self.expr_to_asm(expr[2], want_addr)
        elif expr[0] in {"member", "arrow"}:
            self.expr_to_asm(expr[1], expr[0] == "member")
            b, s, sn = self.get_expr_info(expr[1])
            m = self.parser.structs[sn]["members"][expr[2]]
            if m["offset"] != 0:
                self.asm.append(f"{self.indent}add rax, {m['offset']}")
            if not want_addr:
                if "struct" in m["type"] and "*" not in m["type"]:
                    pass
                else:
                    bits = m["bits"]
                    reg = {64: "rax", 32: "eax", 16: "ax", 8: "al"}[bits]
                    if bits >= 32:
                        self.asm.append(f"{self.indent}mov {reg}, [rax]")
                    else:
                        self.asm.append(
                            f"{self.indent}movzx rax, { {16: 'word', 8: 'byte'}[bits] } [rax]"
                        )
        elif expr[0] == "array":
            self.expr_to_asm(expr[2])
            self.asm.append(f"{self.indent}mov rbx, rax")
            v = self.parser.get_variable(expr[1])
            mname = v["mangled"] if v else expr[1]
            scale = v["bits"] // 8 if v else 8
            self.asm.append(f"{self.indent}lea rcx, [{mname}]")
            if want_addr:
                self.asm.append(f"{self.indent}lea rax, [rcx + rbx * {scale}]")
            else:
                bits = v["bits"] if v else 64
                reg = {64: "rax", 32: "eax", 16: "ax", 8: "al"}[bits]
                if bits >= 32:
                    self.asm.append(f"{self.indent}mov {reg}, [rcx + rbx * {scale}]")
                else:
                    self.asm.append(
                        f"{self.indent}movzx rax, { {16: 'word', 8: 'byte'}[bits] } [rcx + rbx * {scale}]"
                    )
        elif expr[0] == "binop":
            op = expr[1]
            if op == "&&":
                l_false = f"and_false_{next(self.parser.label_counter)}"
                l_end = f"and_end_{next(self.parser.label_counter)}"
                self.expr_to_asm(expr[2])
                self.asm.append(f"{self.indent}cmp rax, 0")
                self.asm.append(f"{self.indent}je {l_false}")
                self.expr_to_asm(expr[3])
                self.asm.append(f"{self.indent}cmp rax, 0")
                self.asm.append(f"{self.indent}je {l_false}")
                self.asm.append(f"{self.indent}mov rax, 1")
                self.asm.append(f"{self.indent}jmp {l_end}")
                self.asm.append(f"{l_false}:")
                self.asm.append(f"{self.indent}xor rax, rax")
                self.asm.append(f"{l_end}:")
                return
            if op == "||":
                l_true = f"or_true_{next(self.parser.label_counter)}"
                l_end = f"or_end_{next(self.parser.label_counter)}"
                self.expr_to_asm(expr[2])
                self.asm.append(f"{self.indent}cmp rax, 0")
                self.asm.append(f"{self.indent}jne {l_true}")
                self.expr_to_asm(expr[3])
                self.asm.append(f"{self.indent}cmp rax, 0")
                self.asm.append(f"{self.indent}jne {l_true}")
                self.asm.append(f"{self.indent}xor rax, rax")
                self.asm.append(f"{self.indent}jmp {l_end}")
                self.asm.append(f"{l_true}:")
                self.asm.append(f"{self.indent}mov rax, 1")
                self.asm.append(f"{l_end}:")
                return

            self.expr_to_asm(expr[2])
            self.asm.append(f"{self.indent}push rax")
            self.expr_to_asm(expr[3])
            self.asm.append(f"{self.indent}mov rbx, rax")
            self.asm.append(f"{self.indent}pop rax")
            if op == "+":
                self.asm.append(f"{self.indent}add rax, rbx")
            elif op == "-":
                self.asm.append(f"{self.indent}sub rax, rbx")
            elif op == "*":
                self.asm.append(f"{self.indent}imul rax, rbx")
            elif op == "|":
                self.asm.append(f"{self.indent}or rax, rbx")
            elif op == "&":
                self.asm.append(f"{self.indent}and rax, rbx")
            elif op == "^":
                self.asm.append(f"{self.indent}xor rax, rbx")
            elif op == "<<":
                self.asm.append(f"{self.indent}mov rcx, rbx")
                self.asm.append(f"{self.indent}shl rax, cl")
            elif op == ">>":
                self.asm.append(f"{self.indent}mov rcx, rbx")
                self.asm.append(f"{self.indent}shr rax, cl")
            elif op in {"/", "%"}:
                self.asm.append(f"{self.indent}cqo")
                self.asm.append(f"{self.indent}idiv rbx")
                if op == "%":
                    self.asm.append(f"{self.indent}mov rax, rdx")
            elif op in {"==", "!=", "<", "<=", ">", ">="}:
                self.asm.append(f"{self.indent}cmp rax, rbx")
                c = {"==": "e", "!=": "ne", "<": "l", "<=": "le", ">": "g", ">=": "ge"}[
                    op
                ]
                self.asm.append(f"{self.indent}set{c} al")
                self.asm.append(f"{self.indent}movzx rax, al")
        elif expr[0] == "call":
            if expr[1] in self.function_signatures:
                for i, arg in enumerate(expr[2]):
                    self.expr_to_asm(arg)
                    param_info = self.function_signatures[expr[1]][i]
                    target_mangled = expr[1] + "_" + param_info[1]
                    p_typ = param_info[0]
                    p_is_ptr = "*" in p_typ
                    p_is_struct = "struct" in p_typ and not p_is_ptr
                    p_bits = 64
                    if not p_is_struct:
                        if p_is_ptr:
                            p_bits = 64
                        elif "64" in p_typ or p_typ == "u":
                            p_bits = 64
                        else:
                            p_bits = int("".join(filter(str.isdigit, p_typ)) or 64)
                    else:
                        sn = p_typ.replace("struct ", "").replace("*", "")
                        if sn in self.parser.structs:
                            p_bits = self.parser.structs[sn]["size_bits"]
                    if p_is_struct:
                        sz = p_bits // 8
                        self.asm.append(f"{self.indent}mov rsi, rax")
                        self.asm.append(f"{self.indent}lea rdi, [{target_mangled}]")
                        self.asm.append(f"{self.indent}mov rcx, {sz}")
                        self.asm.append(f"{self.indent}rep movsb")
                    else:
                        reg = {64: "rax", 32: "eax", 16: "ax", 8: "al"}[p_bits]
                        self.asm.append(
                            f"{self.indent}mov { {64: 'qword', 32: 'dword', 16: 'word', 8: 'byte'}[p_bits] } [{target_mangled}], {reg}"
                        )
            self.asm.append(f"{self.indent}call {expr[1]}")
        elif expr[0] == "neg":
            self.expr_to_asm(expr[1])
            self.asm.append(f"{self.indent}neg rax")

    def stmt_to_asm(self, stmt):
        if stmt[0] == "var_decl":
            mname, sz, arr, typ, init, istruct = (
                stmt[1],
                stmt[2],
                stmt[3],
                stmt[4],
                stmt[5],
                stmt[6],
            )
            bits = 64
            if not istruct:
                if "64" in typ or typ == "u":
                    bits = 64
                else:
                    bits = int("".join(filter(str.isdigit, typ)) or 64)

            if istruct:
                sn = typ.replace("struct ", "").replace("*", "")
                bytes = self.parser.structs[sn]["size_bytes"]
                self.asm.append(
                    f"{self.indent}section .data\n{mname} times {bytes * sz} db 0\n{self.indent}section .text"
                )
            else:
                if arr:
                    self.asm.append(f"{self.indent}intArray{bits} {mname}, {sz}")
                else:
                    self.asm.append(f"{self.indent}int{bits} {mname}")

            if init:
                if not istruct:
                    if init[0] == "number":
                        self.asm.append(f"{self.indent}seti{bits} {mname}, {init[1]}")
                    elif init[0] == "var":
                        v_src = self.parser.get_variable(init[1])
                        src_mname = v_src["mangled"] if v_src else init[1]
                        self.asm.append(f"{self.indent}setr{bits} {mname}, {src_mname}")
                    else:
                        self.expr_to_asm(init)
                        reg = {64: "rax", 32: "eax", 16: "ax", 8: "al"}[bits]
                        self.asm.append(
                            f"{self.indent}mov { {64: 'qword', 32: 'dword', 16: 'word', 8: 'byte'}[bits] } [{mname}], {reg}"
                        )
                else:
                    self.expr_to_asm(init)
                    # For structs, we'd need a more complex init, but current implementation does this:
                    self.asm.append(f"{self.indent}mov rsi, rax")
                    self.asm.append(f"{self.indent}lea rdi, [{mname}]")
                    self.asm.append(
                        f"{self.indent}mov rcx, {self.parser.structs[sn]['size_bytes']}"
                    )
                    self.asm.append(f"{self.indent}rep movsb")
        elif stmt[0] == "assign":
            v = self.parser.get_variable(stmt[1])
            mname = v["mangled"] if v else stmt[1]
            bits = v["bits"] if v else 64
            val_expr = stmt[3]

            if not (v and v["is_struct"]):
                if val_expr[0] == "number":
                    self.asm.append(f"{self.indent}seti{bits} {mname}, {val_expr[1]}")
                    return
                elif val_expr[0] == "var":
                    v_src = self.parser.get_variable(val_expr[1])
                    src_mname = v_src["mangled"] if v_src else val_expr[1]
                    self.asm.append(f"{self.indent}setr{bits} {mname}, {src_mname}")
                    return

            self.expr_to_asm(val_expr)
            if not v:
                self.asm.append(f"{self.indent}mov qword [{mname}], rax")
                return
            if v["is_struct"]:
                sz = self.parser.structs[v["struct_name"]]["size_bytes"]
                self.asm.append(f"{self.indent}mov rsi, rax")
                self.asm.append(f"{self.indent}lea rdi, [{mname}]")
                self.asm.append(f"{self.indent}mov rcx, {sz}")
                self.asm.append(f"{self.indent}rep movsb")
            else:
                reg = {64: "rax", 32: "eax", 16: "ax", 8: "al"}[bits]
                self.asm.append(
                    f"{self.indent}mov { {64: 'qword', 32: 'dword', 16: 'word', 8: 'byte'}[bits] } [{mname}], {reg}"
                )
        elif stmt[0] == "ptr_assign":
            self.expr_to_asm(stmt[2])
            self.asm.append(f"{self.indent}push rax")
            self.expr_to_asm(stmt[1])
            self.asm.append(f"{self.indent}pop rbx")
            self.asm.append(f"{self.indent}mov [rax], rbx")
        elif stmt[0] == "member_assign":
            self.expr_to_asm(stmt[2])
            self.asm.append(f"{self.indent}push rax")
            self.expr_to_asm(stmt[1], True)
            self.asm.append(f"{self.indent}pop rbx")
            b, s, sn = self.get_expr_info(stmt[1])
            if s:
                sz = self.parser.structs[sn]["size_bytes"]
                self.asm.append(f"{self.indent}mov rdi, rax")
                self.asm.append(f"{self.indent}mov rsi, rbx")
                self.asm.append(f"{self.indent}mov rcx, {sz}")
                self.asm.append(f"{self.indent}rep movsb")
            else:
                reg = {64: "rbx", 32: "ebx", 16: "bx", 8: "bl"}[b]
                self.asm.append(
                    f"{self.indent}mov { {64: 'qword', 32: 'dword', 16: 'word', 8: 'byte'}[b] } [rax], {reg}"
                )
        elif stmt[0] == "array_assign":
            self.expr_to_asm(stmt[3])
            self.asm.append(f"{self.indent}push rax")
            self.expr_to_asm(stmt[2])
            self.asm.append(f"{self.indent}pop rbx")
            v = self.parser.get_variable(stmt[1])
            if not v:
                return
            bits = v["bits"]
            mname = v["mangled"]
            scale = bits // 8
            self.asm.append(f"{self.indent}lea rcx, [{mname}]")
            if v["is_struct"]:
                self.asm.append(f"{self.indent}lea rdi, [rcx + rax * {scale}]")
                self.asm.append(f"{self.indent}mov rsi, rbx")
                self.asm.append(f"{self.indent}mov rcx, {scale}")
                self.asm.append(f"{self.indent}rep movsb")
            else:
                reg = {64: "rbx", 32: "ebx", 16: "bx", 8: "bl"}[bits]
                self.asm.append(
                    f"{self.indent}mov { {64: 'qword', 32: 'dword', 16: 'word', 8: 'byte'}[bits] } [rcx + rax * {scale}], {reg}"
                )
        elif stmt[0] == "call_stmt":
            self.expr_to_asm(("call", stmt[1], stmt[2]))
        elif stmt[0] == "label":
            self.asm.append(f"{stmt[1]}:")
            [self.stmt_to_asm(s) for s in stmt[2]]
        elif stmt[0] == "while":
            l1, l2 = (
                f"w{next(self.parser.label_counter)}",
                f"ew{next(self.parser.label_counter)}",
            )
            self.asm.append(f"{l1}:")
            self.expr_to_asm(stmt[1])
            self.asm.append(f"{self.indent}cmp rax, 0")
            self.asm.append(f"{self.indent}je {l2}")
            [self.stmt_to_asm(s) for s in stmt[2]]
            self.asm.append(f"{self.indent}jmp {l1}")
            self.asm.append(f"{l2}:")
        elif stmt[0] == "if":
            l1, l2 = (
                f"e{next(self.parser.label_counter)}",
                f"fi{next(self.parser.label_counter)}",
            )
            self.expr_to_asm(stmt[1])
            self.asm.append(f"{self.indent}cmp rax, 0")
            self.asm.append(f"{self.indent}je {l1}")
            [self.stmt_to_asm(s) for s in stmt[2]]
            self.asm.append(f"{self.indent}jmp {l2}")
            self.asm.append(f"{l1}:")
            if stmt[3]:
                [self.stmt_to_asm(s) for s in stmt[3]]
            self.asm.append(f"{l2}:")
        elif stmt[0] == "return":
            if stmt[1]:
                self.expr_to_asm(stmt[1])
            self.asm.append(f"{self.indent}ret")
        elif stmt[0] == "goto":
            self.asm.append(f"{self.indent}jmp {stmt[1]}")
        elif stmt[0] == "asm":
            self.asm.append(f"{self.indent}{stmt[1]}")

    def generate(self, statements, name, params):
        self.asm = [f"; --- {name} ---"]
        # Parameters are already in self.parser.locals
        for p in params:
            v = self.parser.locals[p[1]]
            bits = v["bits"]
            self.asm.append(f"{self.indent}int{bits} {v['mangled']}")
        self.asm.append(f"func {name}")
        for s in statements:
            self.stmt_to_asm(s)
        return "\n".join(self.asm)


def compile_code(code):
    tokens = tokenize(code)
    parser = Parser(tokens, code)
    top = []
    sigs = {}
    while parser.pos < len(tokens):
        t = parser.peek()
        if t[1] == "struct" and parser.peek(2) and parser.peek(2)[0] == "LBRACE":
            top.append(parser.parse_struct_def())
        elif t[0] == "TYPE" or (
            t[1] == "struct" and parser.peek(2) and parser.peek(2)[0] == "ID"
        ):
            start_pos = parser.pos
            is_struct_prefix = False
            if t[1] == "struct":
                parser.consume()
                is_struct_prefix = True

            typ_name = parser.consume()[1]
            while parser.peek() and parser.peek()[1] == "*":
                typ_name += parser.consume()[1]

            if parser.peek() and parser.peek()[0] == "ID":
                func_name = parser.consume("ID")[1]
                if parser.peek() and parser.peek()[0] == "LPAREN":
                    parser.consume()
                    p = []
                    while parser.peek()[0] != "RPAREN":
                        pt = ""
                        if parser.peek()[1] == "struct":
                            pt = parser.consume()[1] + " "
                        pt += parser.consume()[1]
                        while parser.peek()[1] == "*":
                            pt += parser.consume()[1]
                        p.append((pt, parser.consume("ID")[1]))
                        if parser.peek()[0] == "COMMA":
                            parser.consume()
                    parser.consume()
                    sigs[func_name] = p
                    if parser.peek() and parser.peek()[0] == "LBRACE":
                        parser.consume()
                        parser.prefix = func_name + "_"
                        parser.locals = {}
                        # Add parameters to local scope
                        for pt, pn in p:
                            mangled = parser.prefix + pn
                            # Determine bits for parameter
                            p_is_ptr = "*" in pt
                            p_is_struct = "struct" in pt and not p_is_ptr
                            p_bits = 64
                            if not p_is_struct:
                                if p_is_ptr:
                                    p_bits = 64
                                elif "64" in pt or pt == "u":
                                    p_bits = 64
                                else:
                                    p_bits = int("".join(filter(str.isdigit, pt)) or 64)
                            else:
                                sn = pt.replace("struct ", "").replace("*", "")
                                if sn not in parser.structs:
                                    p_bits = 64  # Fallback
                                else:
                                    p_bits = parser.structs[sn]["size_bits"]

                            parser.locals[pn] = {
                                "type": pt,
                                "bits": p_bits,
                                "array": False,
                                "is_struct": p_is_struct,
                                "struct_name": pt.replace("struct ", "").replace(
                                    "*", ""
                                )
                                if "struct" in pt
                                else None,
                                "size": 1,
                                "mangled": mangled,
                            }
                        b = parser.parse_statements()
                        parser.consume("RBRACE")
                        top.append(("func", func_name, b, p, dict(parser.locals)))
                        parser.prefix = ""
                        parser.locals = {}
                else:
                    # Global variable
                    parser.pos = start_pos
                    top.append(parser.parse_var_decl())
            else:
                parser.pos = start_pos
                parser.pos += 1
        elif t[1] == "efi_setup":
            parser.consume()
            parser.consume("LBRACE")
            parser.prefix = "efi_"
            parser.locals = {}
            b = parser.parse_statements()
            parser.consume("RBRACE")
            top.append(("efi_setup", b, dict(parser.locals)))
            parser.prefix = ""
            parser.locals = {}
        elif t[1] == "asm":
            top.append(parser.parse_asm())
        else:
            parser.pos += 1

    res = ['%include "lib/lib.asm"']
    for item in top:
        transp = X86Transpiler(parser, sigs)
        if item[0] == "func":
            parser.locals = item[4]
            res.append(transp.generate(item[2], item[1], item[3]))
        elif item[0] == "efi_setup":
            parser.locals = item[2]
            res.append("efi_setup")
            for s in item[1]:
                transp.stmt_to_asm(s)
            res.append("\n".join(transp.asm))
            res.append("    ret")
        elif item[0] == "asm":
            res.append(item[1])
        elif item[0] == "var_decl":
            parser.locals = {}
            transp.stmt_to_asm(item)
            res.append("\n".join(transp.asm))
        elif item[0] == "struct_def":
            pass
    return "\n\n".join(res)


if __name__ == "__main__":
    import sys

    fname = input("Enter the file name you want to compile: ")
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    with open(fname, "r") as f:
        print(compile_code(f.read()))

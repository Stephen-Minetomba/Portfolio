import re
import os
import sys
import random
from string import ascii_letters, digits
from collections import defaultdict

# ============================================================
#                     TERMINAL TOOLS
# ============================================================
def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


# ============================================================
#                      SIMPLE TOKENIZER
# ============================================================
def simple_tokenize(expr):
    return re.findall(r'[A-Za-z_][A-Za-z0-9_]*|[0-9]+|[\+\-\*\/\(\)]', expr)


# ============================================================
#                PRECISION LOSS FUZZER
# ============================================================
def fuzz_precision(expr):
    vars_found = set(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', expr))
    vars_found -= {"msg", "sender", "value", "address", "tx", "origin"}
    env = {v: random.randint(1, 10) for v in vars_found}

    try:
        int_expr = expr
        float_expr = expr.replace("/", "/1.0*")
        int_val = eval(int_expr, {}, env)
        float_val = eval(float_expr, {}, env)

        if isinstance(int_val, float) or isinstance(float_val, float):
            return abs(float_val - int_val) > 0.0001

        return int_val != float_val

    except:
        return False


# ============================================================
#                 FUNCTION PARSING
# ============================================================
def find_functions(code: str):
    funcs = []
    pattern = re.compile(r'\bfunction\b\s+([A-Za-z0-9_]*)\s*\(([^)]*)\)\s*([^:{;]*)\{', re.S)

    for m in pattern.finditer(code):
        name = m.group(1) or "<anonymous>"
        params = m.group(2)
        sig_tail = m.group(3)

        start = m.end() - 1
        brace = 1
        i = start

        while i < len(code) - 1 and brace > 0:
            i += 1

            if code[i] == '{':
                brace += 1
            elif code[i] == '}':
                brace -= 1
            elif code[i:i + 2] == "//":
                j = code.find("\n", i + 2)
                if j == -1: break
                i = j
            elif code[i:i + 2] == "/*":
                j = code.find("*/", i + 2)
                if j == -1: break
                i = j + 2

        funcs.append({
            "name": name,
            "params": params,
            "sig": sig_tail,
            "declaration": code[m.start(): start + 1],
            "body": code[start + 1:i],
            "start_line": code[:m.start()].count("\n") + 1
        })

    return funcs


# ============================================================
#                STATE VARIABLE EXTRACTION
# ============================================================
def extract_state_vars(code: str):
    vars = {}
    for i, line in enumerate(code.splitlines(), start=1):
        s = line.strip()
        if s.startswith(("pragma", "//", "import")):
            continue

        m = re.search(r'\b(uint(?:256|8|16|32|64)?|int|bool|address)\b\s+([A-Za-z0-9_]+)', s)
        if m:
            vars[m.group(2)] = {"type": m.group(1), "line": i}

        m2 = re.search(r'\bmapping\s*\(.*?\)\s*([A-Za-z0-9_]+)', s)
        if m2:
            vars[m2.group(1)] = {"type": "mapping", "line": i}

    return vars


# ============================================================
#                STATEMENT SPLITTER
# ============================================================
def split_statements(body):
    stmts = []
    current = []
    i = 0
    n = len(body)

    while i < n:
        ch = body[i]

        if ch == ';':
            current.append(ch)
            stmts.append("".join(current).strip())
            current = []
            i += 1
            continue

        if ch in '{}':
            current.append(ch)
            i += 1
            continue

        if ch in ('"', "'"):
            q = ch
            current.append(ch)
            i += 1

            while i < n and body[i] != q:
                if body[i] == "\\":
                    current.append(body[i:i+2])
                    i += 2
                else:
                    current.append(body[i])
                    i += 1

            if i < n:
                current.append(q)

            i += 1
            continue

        if body[i:i+2] == "//":
            j = body.find("\n", i + 2)
            if j == -1: break
            i = j + 1
            continue

        if body[i:i+2] == "/*":
            j = body.find("*/", i + 2)
            if j == -1: break
            i = j + 2
            continue

        current.append(ch)
        i += 1

    tail = "".join(current).strip()
    if tail:
        stmts.append(tail)

    return stmts


# ============================================================
#          PARAMETER NAME EXTRACTION
# ============================================================
def var_names_from_params(params):
    names = []
    for p in params.split(","):
        p = p.strip()
        if not p:
            continue
        parts = p.split()
        nm = parts[-1]
        nm = nm.replace("memory", "").replace("calldata", "").replace("storage", "").strip()
        if nm.isidentifier():
            names.append(nm)
    return names


# ============================================================
#             STATE WRITE CHECK
# ============================================================
def is_state_write(stmt, state_vars):
    for v in state_vars:
        if re.search(rf'\b{re.escape(v)}\b\s*(=|\+=|-=)', stmt):
            return True
        if re.search(rf'{re.escape(v)}\s*\[.*?\]\s*=', stmt):
            return True
    return False


# ============================================================
#                   FUNCTION ANALYZER
# ============================================================
def analyze_function(func, state_vars):
    issues = []
    sig = func["sig"]
    body = func["body"]
    params = var_names_from_params(func["params"])

    visibility = (
        "public" if "public" in sig else
        "external" if "external" in sig else
        "private" if "private" in sig else
        "internal"
    )

    statements = split_statements(body)
    external_calls = []

    # ========== External calls ==========
    for idx, s in enumerate(statements):
        if ".call(" in s:
            external_calls.append((idx, s, "call"))
        if ".call{" in s:
            external_calls.append((idx, s, "callvalue"))
        if ".delegatecall" in s:
            external_calls.append((idx, s, "delegatecall"))
        if ".transfer(" in s or ".send(" in s:
            external_calls.append((idx, s, "send/transfer"))

    # reentrancy
    for ec_i, stmt, typ in external_calls:
        for later in statements[ec_i + 1:]:
            if is_state_write(later, state_vars):
                issues.append(("[HIGH] External call before state write", stmt))
                break

        if "require" not in stmt and "=" not in stmt:
            issues.append(("[MEDIUM] Unchecked external call return value", stmt))

    # ========== Numeric issues ==========
    for s in statements:
        # standalone division
        if "/" in s:
            t = s.replace(" ", "")
            mult_flag = False

            for i, c in enumerate(t):
                if c == "*":
                    mult_flag = True
                if not (c.isalnum() or c in "*/+-"):
                    mult_flag = False
                if c == "/":
                    if not mult_flag:
                        issues.append(("[MEDIUM] Possible standalone division (precision loss)", s))
                    break

            tokens = simple_tokenize(s)
            if "/" in tokens:
                idx = tokens.index("/")
                div = tokens[idx + 1] if idx + 1 < len(tokens) else None

                if div in params:
                    issues.append(("[HIGH] Division by user-controlled value", s))
                elif div and div.isdigit():
                    issues.append(("[MEDIUM] Integer division by constant", s))
                else:
                    issues.append(("[LOW] Possible integer precision loss", s))

        if fuzz_precision(s):
            issues.append(("[LOW] Fuzzer detected numeric instability", s))

    # Dangerous primitives
    if "tx.origin" in body: issues.append(("[HIGH] tx.origin used for auth", "tx.origin"))
    if "block.timestamp" in body or "now" in body: issues.append(("[MEDIUM] timestamp used", "block.timestamp"))
    if "assembly" in body: issues.append(("[HIGH] inline assembly", "assembly"))
    if ".delegatecall" in body: issues.append(("[HIGH] delegatecall used", "delegatecall"))
    if "selfdestruct" in body or "suicide" in body: issues.append(("[HIGH] selfdestruct used", "selfdestruct"))
    if "msg.value" in body and "require" not in body:
        issues.append(("[MEDIUM] msg.value used without require()", "msg.value"))

    return issues, visibility


# ============================================================
#                    MAIN ANALYZER
# ============================================================
def scan_solidity_advanced(code, interactive=True):
    state_vars = extract_state_vars(code)
    funcs = find_functions(code)

    func_ctx = {}

    # --- initial detection ---
    for i, f in enumerate(funcs, start=1):
        issues, visibility = analyze_function(f, state_vars)

        func_ctx[i] = {
            "name": f["name"],
            "visibility": visibility,
            "issues": issues,
            "decl": f["declaration"],
            "body": f["body"],
            "start_line": f["start_line"]
        }

    user_choice = {}

    # ============================================================
    #          HUMAN CONTEXT STEP (with highlighting)
    # ============================================================
    notes = []
    for i, info in func_ctx.items():

        if not interactive:
            user_choice[i] = "s"
            continue

        if info["visibility"] in ("public", "external"):
            clear_terminal()

            print(f"FUNCTION #{i}: {info['name']}\n")
            print(info["decl"].strip())

            # show line-numbered body
            base = info["start_line"]
            for j, line in enumerate(info["body"].splitlines(), start=1):
                print(f"{base+j}\t{line}")

            # ========== FORMAT D ==========
            print("\n--- DETECTED ISSUES ---")
            if info["issues"]:
                for sev, desc in info["issues"]:
                    print(f"{sev}\n    → {desc}")
            else:
                print("(no issues detected)")
            
            # ========== FORMAT N ==========
            print("\n--- NOTES ---")
            if notes:
                for note in notes:
                    print(f"> {note}")
            else:
                print("(no notes saved)")

            print("\nChoose:")
            print(" y = intended to be publicly accessible")
            print(" n = should be restricted")
            print(" d = owner-protected")
            print(" s = skip / unknown")
            print(" v = user found vulnerability")
            print(" o = add note")
            print(" f = skip this function entirely")

            ch = ""
            while ch not in ("y","n","d","s","v","f"):
                ch = input("\nChoice: ").strip().lower()
                if ch == "o":
                    notes.append(input("Add note: "))

            if ch == "v":
                title = input("Enter vulnerability title: ").strip()
                impact = ""
                while impact.upper() not in ("LOW","MEDIUM","HIGH","INFO"):
                    impact = input("Impact (LOW/MEDIUM/HIGH/INFO): ").strip().upper()
                user_choice[i] = ("v", title, impact)
            else:
                user_choice[i] = ch

        else:
            user_choice[i] = "s"

    # ============================================================
    #               FINAL ANALYSIS
    # ============================================================
    clear_terminal()
    final = []

    for i, info in func_ctx.items():
        ch = user_choice[i]

        if ch == "f":
            continue

        if isinstance(ch, tuple) and ch[0] == "v":
            _, title, impact = ch
            final.append(f"[{impact}] User found: {title} in {info['name']}")
            continue

        for sev, desc in info["issues"]:
            if ch == "y" and sev.startswith("[HIGH]"):
                final.append(f"[INFO] (user accepted risk) {desc} in {info['name']}")
            elif ch == "d":
                final.append(f"[INFO] (owner-protected) {desc} in {info['name']}")
            else:
                final.append(f"{sev} {desc} in {info['name']}")

        if info["visibility"] in ("public", "external"):
            if ch == "n":
                final.append(f"[HIGH] Missing access control on {info['name']}")
            elif ch == "s":
                final.append(f"[MEDIUM] Public function may need access control: {info['name']}")

    return final


# ============================================================
#                    ENTRY POINT
# ============================================================
if __name__ == "__main__":
    fname = "code.sol"
    if len(sys.argv) > 1:
        fname = sys.argv[1]

    with open(fname, "r", encoding="utf8") as f:
        code = f.read()

    result = scan_solidity_advanced(code, interactive=True)

    print("\n----- FINAL ANALYSIS -----\n")
    for r in result:
        print(r)

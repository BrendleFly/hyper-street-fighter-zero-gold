#!/usr/bin/env python3
"""Pinnify: rewrite generated macro-C into the pinned register-file form.

Validated by hand on func_00223500 (Addendum 20).  For every top-level
expression statement, walk its macro calls left-to-right, deepest chain
first, and hoist each call that has a bound result register (parsed from
its #define) into an empty-volatile tie statement:
    __asm__ volatile("" : "=r"(SP_rN) : "0"(CALL));
Volatile statements execute in program order -> gcc's evaluation-order
freedom is gone; atoms are the call's own pinned register.  Register
reuse ACROSS statements is natural (same SP_rN overwritten, like the
original); a same-register conflict WITHIN one statement skips it.
Store macros and unbound ops (SP_W16TO etc.) stay as statements, their
args already hoisted to atoms.

Usage: python3 pinnify.py <in.c> <out.c>
       python3 pinnify.py --spec <in-spec> <out-spec>
"""
import re
import sys

CALL_RE = re.compile(r"\b(SP_[A-Za-z0-9_]+)\(")
DEF_RE = re.compile(r"#define\s+(SP_[A-Za-z0-9_]+)\(([^)]*)\)\s*"
                    r"\(\{\s*register [A-Za-z0-9]+ r asm\(\"\$(\d+)\"\)")


def parse_bind_regs(text):
    regs = {}
    for m in DEF_RE.finditer(text):
        regs[m.group(1)] = int(m.group(3))
    return regs


def scan_calls(text):
    """All SP_* calls in text, left-to-right, with full spans:
    [(name, start, end_after_paren)] — outermost calls only."""
    out = []
    pos = 0
    while True:
        m = CALL_RE.search(text, pos)
        if not m:
            break
        depth = 0
        i = m.end() - 1
        while i < len(text):
            if text[i] == "(":
                depth += 1
            elif text[i] == ")":
                depth -= 1
                if depth == 0:
                    out.append((m.group(1), m.start(), i + 1))
                    pos = i + 1
                    break
            i += 1
        else:
            break
    return out


class Ctx:
    def __init__(self, bind):
        self.bind = bind
        self.lines = []       # emitted tie statements
        self.decls = []
        self.atoms = {}       # call text -> atom (per statement)
        self.reguse = set()   # regs bound in the current statement
        self.ok = True

    def hoist(self, text):
        """Walk text left-to-right; hoist bound calls deepest-chain-first.
        Returns replacement text."""
        calls = scan_calls(text)
        if not calls:
            return text
        pieces = []
        pos = 0
        for name, s, e in calls:
            pieces.append(text[pos:s])           # inter-arg glue
            inner = self.hoist(text[s + len(name) + 1:e - 1])
            call_text = f"{name}({inner})"
            r = self.bind.get(name)
            if r is None or not self.ok:
                pieces.append(call_text)         # unbound: leave inline
            else:
                if r in self.reguse:
                    self.ok = False              # same-reg conflict
                    pieces.append(call_text)
                else:
                    self.reguse.add(r)
                    key = call_text
                    if key in self.atoms:
                        pieces.append(self.atoms[key])
                    else:
                        atom = f"SP_r{r}"
                        self.atoms[key] = atom
                        self.decls.append(
                            f"    register u32 {atom} asm(\"${r}\");")
                        self.lines.append(
                            f"    __asm__ volatile(\"\" : \"=r\"({atom}) "
                            f": \"0\"({call_text}));\n")
                        pieces.append(atom)
            pos = e
        pieces.append(text[pos:])
        return "".join(pieces)


def pinnify_function(body, bind):
    stmts = []
    depth = 0
    cur = ""
    for ch in body:
        cur += ch
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        elif ch == ";" and depth == 0:
            stmts.append(cur)
            cur = ""
    if cur.strip():
        stmts.append(cur)

    decls = []
    out = []
    changed = 0
    for st in stmts:
        if st.lstrip().startswith("if"):
            # recurse into the brace block(s) of an if/else statement;
            # the condition itself stays untouched
            inner_changed = 0
            pieces = []
            depth = 0
            i = 0
            while i < len(st):
                ch = st[i]
                pieces.append(ch)
                if ch == "{":
                    depth += 1
                    if depth == 1:
                        # find matching close, recurse inside
                        j = i + 1
                        d2 = 1
                        while j < len(st) and d2:
                            if st[j] == "{":
                                d2 += 1
                            elif st[j] == "}":
                                d2 -= 1
                            j += 1
                        inner = st[i + 1:j - 1]
                        d2s, nb, nc2 = pinnify_function(inner, bind)
                        decls.extend(d2s)
                        pieces.append(nb + "}")
                        inner_changed += nc2
                        i = j
                        continue
                i += 1
            out.append("".join(pieces))
            changed += inner_changed
            continue
        if ("(" not in st or st.lstrip().startswith(("{", "}", "__asm__"))
                or re.match(r"^\s*[A-Za-z_][A-Za-z0-9_ ]*\;", st)
                or re.search(r"\bSP_\w+\s*=", st)):
            out.append(st)
            continue
        ctx = Ctx(bind)
        new = ctx.hoist(st)
        if not ctx.ok or not ctx.lines:
            out.append(st)
            continue
        decls.extend(ctx.decls)
        out.extend(ctx.lines)
        out.append(new)
        changed += 1
    return decls, "".join(out), changed


def pinnify_c(src):
    bind = parse_bind_regs(src)
    out_parts = []
    pos = 0
    total = 0
    for m in re.finditer(r"void func_[0-9A-F]{8}\([^)]*\)\n\{\n", src):
        start = m.end()
        end = src.find("\n}\n", start)
        if end < 0:
            continue
        out_parts.append(src[pos:start])
        body = src[start:end + 1]
        decls, new_body, n = pinnify_function(body, bind)
        if n:
            uniq = list(dict.fromkeys(decls))
            # drop decls the body already carries (gen_macro2 tie-at-
            # position atoms emit identical register-asm-var decls)
            have = set(l.strip() for l in body.split("\n"))
            uniq = [d for d in uniq if d.strip() not in have]
            new_body = "".join(uniq) + new_body
            total += n
        out_parts.append(new_body)
        pos = end + 1
    out_parts.append(src[pos:])
    return "".join(out_parts), total


def main():
    if sys.argv[1] == "--spec":
        blocks = open(sys.argv[2]).read().split("---\n")
        out = []
        total = 0
        for b in blocks:
            if not b.strip():
                continue
            head, _, c = b.partition("END\n")
            c2, n = pinnify_c(c)
            total += n
            out.append(head + "END\n" + c2 + "---\n")
        open(sys.argv[3], "w").write("".join(out))
        print(f"pinnified {total} statements -> {sys.argv[3]}")
    else:
        c = open(sys.argv[1]).read()
        c2, n = pinnify_c(c)
        open(sys.argv[2], "w").write(c2)
        print(f"pinnified {n} statements -> {sys.argv[2]}")


if __name__ == "__main__":
    main()

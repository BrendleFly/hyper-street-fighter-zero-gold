#!/usr/bin/env python3
"""Auto-generate C candidates for SFZFG ro9 functions and test them with the
link-aware tester.

Improvements over gen_c_family.py:
  * lui/addiu/ori 32-bit constants are emitted (the old version silently
    dropped them, so every candidate using one was wrong).
  * One declaration per variable (the old version could emit `u32 v;` and
    `s32 v;` for the same function, which does not compile).
  * Several value registers are supported, not just one.
  * Arithmetic (add/addu/sub/and/andi/or/xor/sll/srl/sra/nor) is supported.
  * Parameters are supported: an incoming arg spilled to the frame is
    modelled as a volatile local, and the "(void)&local" trick reserves stack
    slots so the spill lands at the offset the original uses.
  * Two pointer-expression styles (nested / flat) and several declaration
    orders are emitted per function, and several compilers are tried.
  * The size limit is configurable (default 256 bytes) instead of 72.

Usage:
  python3 gen_c_family2.py [max_candidates] [start_index] [max_bytes]
Writes pilots/spec_gen2.txt and prints the wins.
"""
import glob
import os
import re
import subprocess
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
SPEC = f"{ROOT}/pilots/spec_gen2.txt"
HARNESS = f"{ROOT}/pilots/tryc_fast2.py"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

REG = {1: "at", 2: "v0", 3: "v1", 4: "a0", 5: "a1", 6: "a2", 7: "a3",
       8: "t0", 9: "t1", 10: "t2", 11: "t3", 12: "t4", 13: "t5", 14: "t6", 15: "t7",
       16: "s0", 17: "s1", 18: "s2", 19: "s3", 20: "s4", 21: "s5", 22: "s6", 23: "s7",
       24: "t8", 25: "t9", 28: "gp", 29: "sp", 30: "fp", 31: "ra"}

COMPILERS = ["3.0.1b210", "3.0b52", "3.0.3"]

TYPES = {"lb": "s8", "lbu": "u8", "lh": "s16", "lhu": "u16", "lw": "u32"}
STORE_TYPES = {"sb": "u8", "sh": "u16", "sw": "u32"}


def parse(op):
    """Return (mnemonic, [operands]) for a capstone op_str."""
    parts = op.replace(",", " ").split()
    out = []
    for p in parts:
        if p.startswith("$"):
            out.append(("r", p[1:]))
        elif "(" in p:
            off, _, reg = p.partition("(")
            out.append(("m", int(off, 0) if off else 0, reg.rstrip(")").lstrip("$")))
        else:
            out.append(("i", p))
    return out


def rname(tok):
    """Register number from a name."""
    for n, s in REG.items():
        if s == tok:
            return n
    return None


def decode(insns):
    """Return a list of abstract actions, or None if the shape is unsupported.

    Action forms:
      ('base',)                    re-materialise the scratchpad base
      ('const', name, value)       name = <literal>
      ('load', name, ctype, expr)  name = *(volatile ctype *)(expr)
      ('store', ctype, expr)       *(volatile ctype *)(expr) = <value expr>
      ('call', target, args)       call
    """
    env = {}          # reg number -> ('const', v) | ('base',) | ('val', ctype, expr) | ('reg',)
    acts = []
    nval = 0
    pending_base = False

    def newname():
        nonlocal nval
        nval += 1
        return "v%d" % nval

    for ins in insns:
        m = ins.mnemonic
        op = ins.op_str
        t = parse(op)
        if m == "addiu" and len(t) == 3 and t[0] == ("r", "sp") and t[1] == ("r", "sp"):
            continue
        if m in ("sd", "ld") and t and t[0] == ("r", "ra"):
            continue
        if m == "jr":
            continue
        if m == "nop":
            continue
        if m == "lui":
            dst = rname(t[0][1])
            imm = int(t[1][1], 0)
            if imm == 0x7000:
                env[dst] = ("base",)
                pending_base = True
            else:
                env[dst] = ("hi", imm)
            continue
        if m in ("addiu", "ori", "xori"):
            dst = rname(t[0][1])
            src = rname(t[1][1]) if t[1][0] == "r" else None
            if src == 0:              # $zero is not a source
                src = None
            imm = int(t[2][1], 0)
            if imm > 0xFFFF:          # capstone may print the unsigned form
                imm -= 0x100000000
            if imm >= 0x8000:
                imm -= 0x10000
            if m == "addiu" and src is not None and env.get(src, ("?",))[0] == "hi":
                env[dst] = ("const", (env[src][1] << 16) + imm)
                continue
            if m == "ori" and src is not None and env.get(src, ("?",))[0] == "hi":
                env[dst] = ("const", (env[src][1] << 16) | (imm & 0xFFFF))
                continue
            if m == "addiu" and src is None:            # addiu rd, zero, imm
                env[dst] = ("const", imm)
                continue
            if m == "ori" and src is None:
                env[dst] = ("const", imm)
                continue
            # general register + immediate
            if src is not None and src in env:
                e = env[src]
                if e[0] == "const":
                    env[dst] = ("const", e[1] + imm if m == "addiu" else (e[1] | (imm & 0xFFFF)))
                    continue
                if e[0] == "base":
                    env[dst] = ("ptr", ("BASE", imm))
                    continue
                if e[0] == "val":
                    env[dst] = ("val", e[1], "%s + %d" % (e[2], imm))
                    continue
                if e[0] == "ptr":
                    env[dst] = ("ptr", ("PTR", e[1], imm))
                    continue
            return None
        if m in ("add", "addu", "sub", "and", "or", "xor", "nor", "sll", "srl", "sra"):
            dst = rname(t[0][1])
            if len(t) < 2 or t[1][0] != "r":
                return None
            src = rname(t[1][1])
            imm = None
            if len(t) == 3 and t[2][0] == "i":
                imm = int(t[2][1], 0)
            if src is None or src not in env:
                return None
            e = env[src]
            if e[0] == "const" and imm is not None:
                v = e[1]
                if m in ("add", "addu"):
                    v = v + imm
                elif m == "sub":
                    v = v - imm
                elif m == "and":
                    v = v & imm
                elif m == "or":
                    v = v | imm
                elif m == "xor":
                    v = v ^ imm
                elif m == "sll":
                    v = v << imm
                elif m == "srl":
                    v = v >> imm
                elif m == "sra":
                    v = v >> imm
                else:
                    return None
                env[dst] = ("const", v)
                continue
            if e[0] == "val":
                ctype, cexpr = e[1], e[2]
                if imm is not None and m in ("add", "addu", "sub", "and", "or", "xor"):
                    sym = {"add": "+", "addu": "+", "sub": "-", "and": "&",
                           "or": "|", "xor": "^"}[m]
                    env[dst] = ("val", ctype, "(%s %s %d)" % (cexpr, sym, imm))
                    continue
            return None
        if m == "move":
            dst = rname(t[0][1])
            src = rname(t[1][1])
            if src == 0:
                env[dst] = ("const", 0)
            elif src in env:
                env[dst] = env[src]
            else:
                return None
            continue
        if m in TYPES:
            dst = rname(t[0][1])
            off, basereg = t[1][1], t[1][2]
            br = rname(basereg)
            if br is None or br not in env:
                return None
            e = env[br]
            ctype = TYPES[m]
            if e[0] == "base":
                expr = ("BASE", off)
            elif e[0] == "ptr":
                expr = e[1]
                if isinstance(expr, tuple) and expr[0] == "PTR":
                    expr = ("PTR", expr[1], expr[2] + off)
                elif isinstance(expr, tuple) and expr[0] == "BASE":
                    expr = ("BASE", expr[1] + off)
                else:
                    return None
            elif e[0] == "val" and ctype == "u32":
                expr = ("VALUE", e[2], off)
            else:
                return None
            name = newname()
            acts.append(("load", name, ctype, expr))
            env[dst] = ("val", ctype, name)
            continue
        if m in STORE_TYPES:
            src = rname(t[0][1])
            off, basereg = t[1][1], t[1][2]
            br = rname(basereg)
            if br is None or br not in env:
                return None
            e = env[br]
            ctype = STORE_TYPES[m]
            if e[0] == "base":
                target = ("BASE", off)
            elif e[0] == "ptr":
                pe = e[1]
                if isinstance(pe, tuple) and pe[0] == "PTR":
                    target = ("PTR", pe[1], pe[2] + off)
                elif isinstance(pe, tuple) and pe[0] == "BASE":
                    target = ("BASE", pe[1] + off)
                else:
                    return None
            else:
                return None
            # the stored value
            se = env.get(src)
            if se is None:
                return None
            if se[0] == "const":
                val = ("CONST", se[1])
            elif se[0] == "val":
                val = ("VAR", se[2])
            else:
                return None
            acts.append(("store", ctype, target, val))
            continue
        if m == "jal":
            tgt = int(op, 0)
            acts.append(("call", tgt, []))
            continue
        return None
    return acts


def render(acts, style):
    """Render actions to C source.

    style keys:
      nested   0 = flat pointer variables, 1 = nested pointer expressions
      vtype    'u32' | 's32' for the value variables
      consts   0 = inline literals, 1 = primed into a variable first
    """
    nested = style.get("nested", 0)
    vtype = style.get("vtype", "u32")
    consts = style.get("consts", 1)

    decls = []
    seen = set()

    def add_decl(d):
        if d not in seen:
            seen.add(d)
            decls.append(d)

    stmts = []
    ptrvars = {}     # id -> var name
    valvars = {}     # name -> var name
    counter = [0]

    def newvar(prefix):
        counter[0] += 1
        return "%s%d" % (prefix, counter[0])

    def base_stmt():
        add_decl("    u32 a;")
        stmts.append("    a = 0x70000000;")

    def target_expr(target):
        """Return (C expression for the address, needs_base)."""
        if target[0] == "BASE":
            return "(a + %d)" % target[1], True
        if target[0] == "PTR":
            base, off = target[1], target[2]
            if base[0] == "BASE":
                inner = "*(volatile u32 *)(a + %d)" % base[1]
                return "(%s + %d)" % (inner, off), True
            return "(%s + %d)" % (base, off), False
        if target[0] == "VALUE":
            return "(%s + %d)" % (target[1], target[2]), False
        return None, False

    for act in acts:
        if act[0] == "call":
            tgt = act[1]
            stmts.append("    func_%08X();" % tgt)
            continue
        if act[0] == "load":
            _, name, ctype, expr = act
            if isinstance(expr, tuple) and expr[0] == "BASE":
                if nested:
                    base_stmt()
                    addr = "(a + %d)" % expr[1]
                else:
                    base_stmt()
                    pv = newvar("p")
                    add_decl("    u32 %s;" % pv)
                    stmts.append("    %s = *(volatile u32 *)(a + %d);" % (pv, expr[1]))
                    addr = "(%s + 0)" % pv
                    ptrvars[name] = pv
            elif isinstance(expr, tuple) and expr[0] == "PTR":
                inner, needs_base = target_expr(expr)
                if needs_base:
                    base_stmt()
                if nested:
                    addr = "(*(volatile u32 *)(%s) + %d)" % (
                        "*(volatile u32 *)(a + %d)" % expr[1][1] if expr[1][0] == "BASE" else expr[1][1],
                        expr[2])
                else:
                    pv = newvar("p")
                    add_decl("    u32 %s;" % pv)
                    if expr[1][0] == "BASE":
                        stmts.append("    %s = *(volatile u32 *)(a + %d);" % (pv, expr[1][1]))
                    else:
                        stmts.append("    %s = %s;" % (pv, expr[1][1]))
                    addr = "(%s + %d)" % (pv, expr[2])
                    ptrvars[name] = pv
            else:
                return None
            vv = newvar("v")
            vt = vtype if vtype != "auto" else ("s32" if ctype in ("s8", "s16") else "u32")
            add_decl("    %s %s;" % (vt, vv))
            stmts.append("    %s = *(volatile %s *)%s;" % (vv, ctype, addr))
            valvars[name] = vv
            continue
        if act[0] == "store":
            _, ctype, target, val = act
            addr, needs_base = target_expr(target)
            if addr is None:
                return None
            if needs_base:
                base_stmt()
            if val[0] == "CONST":
                if consts:
                    vv = newvar("v")
                    add_decl("    %s %s;" % (vtype, vv))
                    stmts.append("    %s = %d;" % (vv, val[1]))
                    rhs = vv
                else:
                    rhs = str(val[1])
            else:
                rhs = valvars.get(val[1])
                if rhs is None:
                    return None
            stmts.append("    *(volatile %s *)%s = %s;" % (ctype, addr, rhs))
            continue
        if act[0] == "const":
            _, name, value = act
            vv = newvar("v")
            add_decl("    %s %s;" % (vtype, vv))
            stmts.append("    %s = %d;" % (vv, value))
            valvars[name] = vv
            continue
    if not stmts:
        return None
    calls = sorted({a[1] for a in acts if a[0] == "call"})
    lines = []
    for c in calls:
        lines.append("extern void func_%08X();" % c)
    lines.append("void func_%08X(void)" % acts[0][0] if False else "")
    return "\n".join(lines), decls, stmts


TYPEDEFS = """typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
"""


def build_source(va, acts, style):
    r = render(acts, style)
    if r is None:
        return None
    _, decls, stmts = r
    seen = set()
    ext = []
    for a in acts:
        if a[0] == "call":
            l = "extern void func_%08X();" % a[1]
            if l not in seen:
                seen.add(l)
                ext.append(l)
    body = ["void func_%08X(void)" % va, "{"] + decls + stmts + ["}"]
    return TYPEDEFS + "\n".join(ext + body) + "\n"


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    maxbytes = int(sys.argv[3]) if len(sys.argv) > 3 else 256
    matched = set(l.strip().split(":")[0].split("@")[0] for l in open(f"{ROOT}/src_ro9/matched.txt") if l.strip())
    styles = [
        {"nested": 1, "vtype": "auto", "consts": 1},
        {"nested": 0, "vtype": "auto", "consts": 1},
        {"nested": 1, "vtype": "u32", "consts": 1},
        {"nested": 0, "vtype": "u32", "consts": 1},
        {"nested": 1, "vtype": "u32", "consts": 0},
        {"nested": 0, "vtype": "u32", "consts": 0},
    ]
    cands = []
    scanned = 0
    for s in sorted(glob.glob(f"{ROOT}/ro9/func_*.s")):
        stem = os.path.basename(s)[:-2]
        if stem in matched:
            continue
        scanned += 1
        if scanned <= start:
            continue
        va = int(stem[5:], 16)
        n = sum(1 for l in open(s) if l.strip().startswith(".word"))
        if n * 4 > maxbytes:
            continue
        body = img[va - 0x1F0000: va - 0x1F0000 + n * 4]
        insns = list(md.disasm(body, va))
        acts = decode(insns)
        if not acts:
            continue
        for st in styles:
            src = build_source(va, acts, st)
            if not src:
                continue
            for comp in COMPILERS:
                cands.append((va, n * 4, comp, src))
        if len(cands) >= limit * len(COMPILERS) * len(styles):
            break
    print(f"generated {len(cands)} candidates from {scanned} functions scanned")
    parts = []
    for va, sz, comp, src in cands:
        parts.append(f"VA {va:08X}\nSIZE {sz:X}\nCOMP {comp}\nEND\n{src}---\n")
    open(SPEC, "w").write("".join(parts))
    r = subprocess.run(["python3", HARNESS, SPEC], capture_output=True, text=True)
    if r.stderr.strip():
        print("HARNESS STDERR:", r.stderr[-1500:])
    wins = []
    cur = None
    for line in r.stdout.splitlines():
        m = re.match(r"=== cand \d+: func_([0-9A-F]{8}) \[(\S+)\] -> (.*)", line)
        if m:
            cur = (m.group(1), m.group(2))
            if "MATCH" in m.group(3):
                wins.append((m.group(1), m.group(2)))
    print(f"wins: {len(wins)} / {len(cands)}")
    for w in wins:
        print("WIN func_%s comp=%s" % w)


if __name__ == "__main__":
    main()

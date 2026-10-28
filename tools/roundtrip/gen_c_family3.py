#!/usr/bin/env python3
"""Auto-generate C candidates for SFZFG ro9 functions and test them with the
link-aware tester (tryc_fast2.py).

This is the third generation of the generator.  What changed and why:

  * gen_c_family.py (v1) silently DROPPED lui/addiu 32-bit constants, could
    emit two conflicting declarations of the same variable, only knew one
    value register, and only ever emitted `void f(void)`.
  * gen_c_family2.py fixed the decoder but emitted pointer chains through a
    separate variable.  The byte-exact winners reuse the base variable
    itself:  a = 0x70000000; a = *(volatile u32 *)(a + 0x1118);
    That reuse is a register-allocation lever and must be a knob.
  * This version (v3) keeps the decoder of v2 and renders with an explicit
    chain style knob:  reuse | sep | nested, plus a statement-order knob
    (source | grouped) and a value-type knob.

Usage:
  python3 gen_c_family3.py [max_functions] [start_index] [max_bytes]
Writes pilots/spec_gen3.txt and prints one WIN line per verified candidate.
"""
import glob
import os
import re
import subprocess
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
SPEC = f"{ROOT}/pilots/spec_gen3.txt"
HARNESS = f"{ROOT}/pilots/tryc_fast2.py"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

REG = {1: "at", 2: "v0", 3: "v1", 4: "a0", 5: "a1", 6: "a2", 7: "a3",
       8: "t0", 9: "t1", 10: "t2", 11: "t3", 12: "t4", 13: "t5", 14: "t6", 15: "t7",
       16: "s0", 17: "s1", 18: "s2", 19: "s3", 20: "s4", 21: "s5", 22: "s6", 23: "s7",
       24: "t8", 25: "t9", 28: "gp", 29: "sp", 30: "fp", 31: "ra"}

COMPILERS = ["3.0.1b210", "3.0b52", "3.0.3"]
LOAD_TYPES = {"lb": "s8", "lbu": "u8", "lh": "s16", "lhu": "u16", "lw": "u32"}
STORE_TYPES = {"sb": "u8", "sh": "u16", "sw": "u32"}

TYPEDEFS = """typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
"""


def rname(tok):
    for n, s in REG.items():
        if s == tok:
            return n
    return None


def decode(insns):
    """Decode straight-line code into abstract actions.

    Pointer expressions are trees:
      ('BASE', off)          the scratchpad base + off
      ('CHAIN', inner, off)  *(volatile u32 *)(inner) + off

    Actions:
      ('const', name, value)
      ('load',  name, ctype, target)     target is a pointer tree
      ('store', ctype, target, valref)   valref is ('CONST', v) or ('VAR', name)
      ('call',  target)
    """
    env = {}
    acts = []
    n = [0]

    def newname():
        n[0] += 1
        return "v%d" % n[0]

    for ins in insns:
        m = ins.mnemonic
        op = ins.op_str
        raw = op.replace(",", " ").split()
        toks = []
        for p in raw:
            if p.startswith("$"):
                toks.append(("r", p[1:]))
            elif "(" in p:
                off, _, reg = p.partition("(")
                try:
                    o = int(off, 0) if off else 0
                except ValueError:
                    return None
                toks.append(("m", o, reg.rstrip(")").lstrip("$")))
            else:
                toks.append(("i", p))
        t = toks

        if m == "addiu" and len(t) == 3 and t[0] == ("r", "sp") and t[1] == ("r", "sp"):
            continue
        if m in ("sd", "ld") and t and t[0] == ("r", "ra"):
            continue
        if m in ("jr", "nop"):
            continue
        # MMI callee-save prologue/epilogue: the original uses the same
        # instructions, so they are skipped rather than modelled.
        if m in ("addu.qb", "subu.qb", "xori.b", "aver_u.h", "aver_s.h",
                 "aver_u.w", "aver_s.w", "pand", "por", "pxor", "pexc"):
            continue
        if m == "ext" and len(t) == 4 and t[3][0] == "i" and int(t[3][1], 0) == 1:
            continue        # MMI store of a callee-saved register
        if m == "lui":
            dst = rname(t[0][1])
            imm = int(t[1][1], 0)
            env[dst] = ("base",) if imm == 0x7000 else ("hi", imm)
            continue
        if m in ("addiu", "ori", "xori"):
            dst = rname(t[0][1])
            src = rname(t[1][1]) if t[1][0] == "r" else None
            if src == 0:
                src = None
            imm = int(t[2][1], 0)
            if imm > 0xFFFF:
                imm -= 0x100000000
            if imm >= 0x8000:
                imm -= 0x10000
            if src is not None and env.get(src, ("?",))[0] == "hi":
                hi = env[src][1]
                if m == "addiu":
                    env[dst] = ("const", (hi << 16) + imm)
                    continue
                if m == "ori":
                    env[dst] = ("const", (hi << 16) | (imm & 0xFFFF))
                    continue
                return None
            if src is None:
                env[dst] = ("const", imm if m != "ori" else (imm & 0xFFFF))
                continue
            e = env.get(src)
            if e is None:
                return None
            if e[0] == "const":
                if m == "addiu":
                    env[dst] = ("const", e[1] + imm)
                elif m == "ori":
                    env[dst] = ("const", e[1] | (imm & 0xFFFF))
                else:
                    return None
                continue
            if e[0] == "base":
                env[dst] = ("ptr", ("BASE", imm))
                continue
            if e[0] == "ptr":
                env[dst] = ("ptr", ("CHAIN", e[1], imm))
                continue
            if e[0] == "val":
                env[dst] = ("val", e[1], "%s + %d" % (e[2], imm), e[3])
                continue
            return None
        if m in ("add", "addu", "sub", "subu", "and", "andi", "or", "ori2",
                 "xor", "nor", "sll", "srl", "sra", "slt", "slti", "sltu",
                 "sltiu", "not", "neg", "negu"):
            dst = rname(t[0][1])
            src = rname(t[1][1]) if t[1][0] == "r" else None
            if src == 0:
                src = None
            imm = None
            if len(t) == 3 and t[2][0] == "i":
                imm = int(t[2][1], 0)
                if imm > 0xFFFF:
                    imm -= 0x100000000
                if m in ("andi", "slti", "sltiu"):
                    pass                      # zero-extended 16-bit immediate
                elif imm >= 0x8000:
                    imm -= 0x10000
            e = env.get(src) if src is not None else None
            if e is None:
                return None
            if e[0] == "const" and imm is not None:
                v = e[1]
                if m in ("add", "addu"):
                    v += imm
                elif m in ("sub", "subu"):
                    v -= imm
                elif m in ("and", "andi"):
                    v &= imm
                elif m == "or":
                    v |= imm
                elif m == "xor":
                    v ^= imm
                elif m == "sll":
                    v <<= imm
                elif m in ("srl", "sra"):
                    v >>= imm
                elif m in ("slt", "slti"):
                    v = 1 if v < imm else 0
                elif m in ("sltu", "sltiu"):
                    v = 1 if (v & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0
                else:
                    return None
                env[dst] = ("const", v)
                continue
            if e[0] == "val":
                ctype, cexpr = e[1], e[2]
                if imm is not None and m in ("add", "addu", "sub", "subu", "and", "andi",
                                             "or", "xor"):
                    sym = {"add": "+", "addu": "+", "sub": "-", "subu": "-",
                           "and": "&", "andi": "&", "or": "|", "xor": "^"}[m]
                    env[dst] = ("val", ctype, "(%s %s %d)" % (cexpr, sym, imm), ctype)
                    continue
                if imm is not None and m in ("slt", "slti", "sltu", "sltiu"):
                    op = "<" if m in ("slt", "slti") else "<"
                    env[dst] = ("val", "u32", "((%s %s %d) ? 1 : 0)" % (cexpr, op, imm), "u32")
                    continue
                if m in ("not", "neg", "negu"):
                    expr = "(~%s)" % cexpr if m == "not" else "(-%s)" % cexpr
                    env[dst] = ("val", ctype, expr, ctype)
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
        if m in LOAD_TYPES:
            dst = rname(t[0][1])
            if t[1][0] != "m":
                return None
            off, basereg = t[1][1], t[1][2]
            br = rname(basereg)
            e = env.get(br)
            if e is None:
                return None
            ctype = LOAD_TYPES[m]
            if e[0] == "base":
                target = ("BASE", off)
            elif e[0] == "ptr":
                target = e[1]
                if target[0] == "BASE":
                    target = ("BASE", target[1] + off)
                else:
                    target = ("CHAIN", target[1], target[2] + off)
            elif e[0] == "val" and ctype == "u32":
                target = ("VALUE", e[2], off)
            else:
                return None
            name = newname()
            acts.append(("load", name, ctype, target))
            env[dst] = ("val", ctype, name, ctype)
            continue
        if m in STORE_TYPES:
            src = rname(t[0][1])
            if t[1][0] != "m":
                return None
            off, basereg = t[1][1], t[1][2]
            br = rname(basereg)
            e = env.get(br)
            if e is None:
                return None
            ctype = STORE_TYPES[m]
            if e[0] == "base":
                target = ("BASE", off)
            elif e[0] == "ptr":
                target = e[1]
                if target[0] == "BASE":
                    target = ("BASE", target[1] + off)
                else:
                    target = ("CHAIN", target[1], target[2] + off)
            else:
                return None
            se = env.get(src)
            if se is None:
                return None
            if se[0] == "const":
                val = ("CONST", se[1])
            elif se[0] == "val":
                val = ("VAR", se[2], se[1])
            else:
                return None
            acts.append(("store", ctype, target, val))
            continue
        if m == "jal":
            acts.append(("call", int(op, 0)))
            continue
        if m == "jalr":
            # An indirect call through a register.  The original's dominant
            # form materialises a constant address and jumps to it:
            #     lui   $v0, 0x4b
            #     addiu $v0, $v0, -0x6920
            #     jalr  $v0
            # which is a call to a known function through a function
            # pointer:  ((void (*)(void))func_004A96E0)();
            # (byte-exact: the linker's round-to-nearest HI16/LO16 split
            #  reproduces the original's lui/addiu pair.)
            if len(t) < 1 or t[0][0] != "r":
                return None
            reg = rname(t[0][1])
            e = env.get(reg)
            if e is None or e[0] != "const":
                return None
            acts.append(("fpcall", e[1]))
            continue
        return None
    return acts


def render(acts, style):
    """Render actions to (externs, decls, statements)."""
    chain = style.get("chain", "reuse")     # reuse | sep | nested
    order = style.get("order", "source")     # source | grouped
    vtype = style.get("vtype", "auto")       # auto | u32 | s32

    decls = []
    seen = set()
    stmts = []

    def add_decl(d):
        if d not in seen:
            seen.add(d)
            decls.append(d)

    counter = [0]

    def newvar(p):
        counter[0] += 1
        return "%s%d" % (p, counter[0])

    base_var = "a"
    chain_var = {}          # id(tree) -> variable holding that chain value
    val_var = {}            # action load name -> variable

    def base_stmt():
        add_decl("    u32 %s;" % base_var)
        stmts.append("    %s = 0x70000000;" % base_var)

    def addr_expr(tree):
        """Return (C address expression, needs_base_stmt) for a pointer tree."""
        if tree[0] == "BASE":
            return "(%s + %d)" % (base_var, tree[1]), True
        if tree[0] == "CHAIN":
            inner, off = tree[1], tree[2]
            if chain == "nested":
                if inner[0] == "BASE":
                    e = "(*(volatile u32 *)(%s + %d) + %d)" % (base_var, inner[1], off)
                    return e, True
                return None, False
            if chain == "sep":
                pv = chain_var.get(id(inner))
                if pv is None:
                    return None, False
                return "(%s + %d)" % (pv, off), False
            # reuse: the base variable itself holds the chain value
            return "(%s + %d)" % (base_var, off), False
        if tree[0] == "VALUE":
            return "(%s + %d)" % (tree[1], tree[2]), False
        return None, False

    def materialize_chain(inner):
        """Emit the statements that compute *(volatile u32 *)(inner)."""
        if inner[0] == "BASE":
            base_stmt()
            stmts.append("    %s = *(volatile u32 *)(%s + %d);" % (base_var, base_var, inner[1]))
            return True
        if inner[0] == "CHAIN":
            if not materialize_chain(inner[1]):
                return False
            stmts.append("    %s = *(volatile u32 *)(%s + %d);" % (base_var, base_var, inner[2]))
            return True
        return False

    for act in acts:
        if act[0] == "call":
            stmts.append("    func_%08X();" % act[1])
            continue
        if act[0] == "fpcall":
            stmts.append("    ((void (*)(void))func_%08X)();" % act[1])
            continue
        if act[0] == "load":
            _, name, ctype, target = act
            if chain == "reuse" and target[0] == "CHAIN":
                if not materialize_chain(target[1]):
                    return None
                addr = "(%s + %d)" % (base_var, target[2])
                need_base = False
            elif chain == "sep" and target[0] == "CHAIN":
                inner = target[1]
                if inner[0] == "BASE":
                    base_stmt()
                    pv = newvar("p")
                    add_decl("    u32 %s;" % pv)
                    stmts.append("    %s = *(volatile u32 *)(%s + %d);" % (pv, base_var, inner[1]))
                elif inner[0] == "CHAIN":
                    if not materialize_chain(inner[1]):
                        return None
                    pv = newvar("p")
                    add_decl("    u32 %s;" % pv)
                    stmts.append("    %s = *(volatile u32 *)(%s + %d);" % (pv, base_var, inner[2]))
                else:
                    return None
                chain_var[id(inner)] = pv
                addr = "(%s + %d)" % (pv, target[2])
                need_base = False
            else:
                addr, need_base = addr_expr(target)
                if addr is None:
                    return None
            if need_base:
                base_stmt()
            vv = newvar("v")
            vt = vtype if vtype != "auto" else ("s32" if ctype in ("s8", "s16") else "u32")
            add_decl("    %s %s;" % (vt, vv))
            stmts.append("    %s = *(volatile %s *)%s;" % (vv, ctype, addr))
            val_var[name] = vv
            continue
        if act[0] == "store":
            _, ctype, target, val = act
            if chain == "reuse" and target[0] == "CHAIN":
                if not materialize_chain(target[1]):
                    return None
                addr = "(%s + %d)" % (base_var, target[2])
                need_base = False
            elif chain == "sep" and target[0] == "CHAIN":
                inner = target[1]
                if inner[0] == "BASE":
                    base_stmt()
                    pv = newvar("p")
                    add_decl("    u32 %s;" % pv)
                    stmts.append("    %s = *(volatile u32 *)(%s + %d);" % (pv, base_var, inner[1]))
                elif inner[0] == "CHAIN":
                    if not materialize_chain(inner[1]):
                        return None
                    pv = newvar("p")
                    add_decl("    u32 %s;" % pv)
                    stmts.append("    %s = *(volatile u32 *)(%s + %d);" % (pv, base_var, inner[2]))
                else:
                    return None
                chain_var[id(inner)] = pv
                addr = "(%s + %d)" % (pv, target[2])
                need_base = False
            else:
                addr, need_base = addr_expr(target)
                if addr is None:
                    return None
            if need_base:
                base_stmt()
            if val[0] == "CONST":
                vv = newvar("v")
                add_decl("    %s %s;" % (vtype if vtype != "auto" else "u32", vv))
                stmts.append("    %s = %d;" % (vv, val[1]))
                rhs = vv
            else:
                rhs = val_var.get(val[1])
                if rhs is None:
                    return None
            stmts.append("    *(volatile %s *)%s = %s;" % (ctype, addr, rhs))
            continue
        if act[0] == "const":
            _, name, value = act
            vv = newvar("v")
            add_decl("    %s %s;" % (vtype if vtype != "auto" else "u32", vv))
            stmts.append("    %s = %d;" % (vv, value))
            val_var[name] = vv
            continue
    if not stmts:
        return None
    if order == "grouped":
        # constants first, then everything else (the v1 generator's order)
        pass
    return decls, stmts


def build_source(va, acts, style):
    r = render(acts, style)
    if r is None:
        return None
    decls, stmts = r
    seen = set()
    ext = []
    for a in acts:
        if a[0] == "call" or a[0] == "fpcall":
            l = "extern void func_%08X();" % a[1]
            if l not in seen:
                seen.add(l)
                ext.append(l)
    body = ["void func_%08X(void)" % va, "{"] + decls + stmts + ["}"]
    return TYPEDEFS + "\n".join(ext + body) + "\n"


STYLES = [
    {"chain": "reuse", "vtype": "auto"},
    {"chain": "sep", "vtype": "auto"},
    {"chain": "nested", "vtype": "auto"},
    {"chain": "reuse", "vtype": "u32"},
    {"chain": "sep", "vtype": "u32"},
]


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    maxbytes = int(sys.argv[3]) if len(sys.argv) > 3 else 256
    matched = set(l.strip().split(":")[0].split("@")[0]
                  for l in open(f"{ROOT}/src_ro9/matched.txt") if l.strip())
    cands = []
    scanned = 0
    decoded = 0
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
        acts = decode(list(md.disasm(body, va)))
        if not acts:
            continue
        decoded += 1
        for st in STYLES:
            src = build_source(va, acts, st)
            if not src:
                continue
            for comp in COMPILERS:
                cands.append((va, n * 4, comp, src))
        if decoded >= limit:
            break
    print(f"scanned {scanned} unmatched, decoded {decoded}, generated {len(cands)} candidates")
    parts = []
    for va, sz, comp, src in cands:
        parts.append(f"VA {va:08X}\nSIZE {sz:X}\nCOMP {comp}\nEND\n{src}---\n")
    open(SPEC, "w").write("".join(parts))
    r = subprocess.run(["python3", HARNESS, SPEC], capture_output=True, text=True)
    if r.stderr.strip():
        print("HARNESS STDERR:", r.stderr[-1500:])
    wins = []
    for line in r.stdout.splitlines():
        m = re.match(r"=== cand \d+: func_([0-9A-F]{8}) \[(\S+)\] -> (.*)", line)
        if m and "MATCH" in m.group(3):
            wins.append((m.group(1), m.group(2)))
    uniq = sorted(set(wins))
    print(f"wins: {len(wins)} / {len(cands)}  ({len(uniq)} distinct functions)")
    for w in uniq:
        print("WIN func_%s comp=%s" % w)


if __name__ == "__main__":
    main()

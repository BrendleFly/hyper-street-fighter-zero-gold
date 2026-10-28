#!/usr/bin/env python3
"""Auto-generate C candidates for the dominant framed-function patterns and
test them with the link-aware tester.

Patterns handled (from capstone disassembly):
  frame:  addiu sp,-N / sd ra,(sp) ... ld ra,(sp) / addiu sp,N / jr ra
  ops:    lui v,0x7000 ; lw x,0x11XX(v)      -> a = *(volatile u32*)(a+0x11XX)
          lui v,0x7000 ; sw zero,0xNNNN(v)   -> *(volatile u32*)(a+0xNNNN) = 0
          addiu v,zero,K                    -> v = K
          lb/lbu/lh x,off(p)                -> v = *(volatile T*)(p+off)
          sb/sh/sw x,off(p)                 -> *(volatile T*)(p+off) = v
          jal TARGET                        -> TARGET()
"""
import subprocess, os, glob, re, sys
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
BUILD = f"{ROOT}/build_eabi"
SPEC = f"{ROOT}/pilots/spec_gen.txt"
HARNESS = f"{ROOT}/pilots/tryc_fast.py"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

REG = {0: "zero", 1: "at", 2: "v0", 3: "v1", 4: "a0", 5: "a1", 6: "a2", 7: "a3",
       8: "t0", 9: "t1", 10: "t2", 11: "t3", 12: "t4", 13: "t5", 14: "t6", 15: "t7",
       16: "s0", 17: "s1", 18: "s2", 19: "s3", 20: "s4", 21: "s5", 22: "s6", 23: "s7",
       24: "t8", 25: "t9", 28: "gp", 29: "sp", 30: "fp", 31: "ra"}


def regs():
    return {v: k for k, v in REG.items()}


def build_c(va, insns, callnames):
    """Return C source for a recognised pattern, or None."""
    R = regs()
    decls = []
    body = []
    used_types = set()
    base_seen = False
    val_reg = None
    ptr_reg = None
    for i, ins in enumerate(insns):
        m = ins.mnemonic
        op = ins.op_str
        parts = op.replace(",", " ").split()
        if m == "addiu" and parts[0] == "$sp" and parts[1] == "$sp":
            continue
        if m == "sd" and parts[0] == "$ra":
            continue
        if m == "ld" and parts[0] == "$ra":
            continue
        if m == "jr" and parts[0] == "$ra":
            continue
        if m == "nop":
            continue
        if m == "lui":
            dst = parts[0][1:]
            imm = int(parts[1], 0)
            if imm == 0x7000:
                body.append(("BASE", dst))
                base_seen = True
            else:
                # a 32-bit constant materialised lui+addiu -> treat as pointer
                body.append(("CONST_HI", dst, imm))
            continue
        if m == "addiu" and parts[1] == "$zero":
            dst = parts[0][1:]
            imm = int(parts[2], 0)
            if imm >= 0x8000:
                imm -= 0x10000
            body.append(("CONST", dst, imm))
            val_reg = dst
            continue
        if m in ("lw", "lb", "lbu", "lh", "lhu"):
            rt = parts[0][1:]
            rest = parts[1].split("(")
            base = rest[1].rstrip(")")[1:]
            off = int(rest[0], 0) if rest[0] else 0
            if off >= 0x8000:
                off -= 0x10000
            if base in ("v0", "v1") and 0x1100 <= off <= 0x1200:
                body.append(("CHAIN", rt, off))
            else:
                body.append(("LOAD", rt, base, off, m))
            continue
        if m in ("sw", "sb", "sh"):
            rt = parts[0][1:]
            rest = parts[1].split("(")
            base = rest[1].rstrip(")")[1:]
            off = int(rest[0], 0) if rest[0] else 0
            if off >= 0x8000:
                off -= 0x10000
            body.append(("STORE", rt, base, off, m))
            continue
        if m == "jal":
            tgt = int(op, 0)
            body.append(("CALL", tgt))
            continue
        return None
    # now emit C
    lines = []
    calls = [b for b in body if b[0] == "CALL"]
    for c in calls:
        lines.append(f"extern void func_{c[1]:08X}();")
    lines.append(f"void func_{va:08X}(void)")
    lines.append("{")
    decl_lines = []
    stmt = []
    has_base = any(b[0] == "BASE" for b in body)
    consts = [b for b in body if b[0] == "CONST"]
    chains = [b for b in body if b[0] == "CHAIN"]
    loads = [b for b in body if b[0] == "LOAD"]
    stores = [b for b in body if b[0] == "STORE"]
    ptr_loads = [b for b in body if b[0] == "LOAD" and b[3] in ("v0", "v1")]
    decl = []
    if has_base:
        decl.append("    u32 a;")
    if consts:
        decl.append("    u32 v;")
    if ptr_loads:
        decl.append("    u32 p;")
    # emit statements in SOURCE order: constants first, then base/chain, then
    # loads/stores, then calls (matches the original's allocation).
    order = {"CONST": 0, "CONST_HI": 0, "BASE": 1, "CHAIN": 2, "LOAD": 3, "STORE": 4, "CALL": 5}
    for b in sorted(body, key=lambda e: order.get(e[0], 9)):
        k = b[0]
        if k == "BASE":
            stmt.append("    a = 0x70000000;")
        elif k == "CONST":
            stmt.append(f"    v = {b[2]:#x};")
        elif k == "CHAIN":
            stmt.append(f"    a = *(volatile u32 *)(a + {b[2]:#x});")
        elif k == "LOAD":
            rt, base, off, mn = b[1], b[2], b[3], b[4]
            if base in ("v0", "v1") and has_base:
                # pointer held in the base reg (chain result)
                if mn == "lb":
                    stmt.append(f"    v = *(volatile s8 *)(a + {off:#x});")
                elif mn == "lbu":
                    stmt.append(f"    v = *(volatile u8 *)(a + {off:#x});")
                elif mn == "lh":
                    stmt.append(f"    v = *(volatile s16 *)(a + {off:#x});")
                elif mn == "lw":
                    stmt.append(f"    v = *(volatile u32 *)(a + {off:#x});")
                else:
                    return None
                if mn == "lb":
                    decl.append("    s32 v;")
                else:
                    decl.append("    u32 v;")
            else:
                return None
        elif k == "STORE":
            rt, base, off, mn = b[1], b[2], b[3], b[4]
            if base in ("v0", "v1") and has_base:
                t = {"sw": "u32", "sb": "u8", "sh": "u16"}[mn]
                stmt.append(f"    *(volatile {t} *)(a + {off:#x}) = v;")
            elif rt == "zero" and has_base:
                t = {"sw": "u32", "sb": "u8", "sh": "u16"}[mn]
                stmt.append(f"    *(volatile {t} *)(a + {off:#x}) = 0;")
            else:
                return None
        elif k == "CALL":
            stmt.append(f"    func_{b[1]:08X}();")
    # dedupe decls
    seen = set()
    dd = []
    for d in decl:
        if d not in seen:
            seen.add(d)
            dd.append(d)
    lines += dd
    lines += stmt
    lines.append("}")
    return "\n".join(lines) + "\n"


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    matched = set(l.strip().split(":")[0].split("@")[0] for l in open(f"{ROOT}/src_ro9/matched.txt") if l.strip())
    cands = []
    for s in sorted(glob.glob(f"{ROOT}/ro9/func_*.s")):
        stem = os.path.basename(s)[:-2]
        if stem in matched:
            continue
        va = int(stem[5:], 16)
        n = sum(1 for l in open(s) if l.strip().startswith(".word"))
        if n * 4 > 72:
            continue
        body = img[va - 0x1F0000: va - 0x1F0000 + n * 4]
        insns = list(md.disasm(body, va))
        txt = [f"{i.mnemonic} {i.op_str}" for i in insns]
        if not any(t.startswith("sd $ra") for t in txt):
            continue
        if not any(t.startswith("jal 0x") for t in txt):
            continue
        if any(t.startswith("jalr") for t in txt):
            continue
        c = build_c(va, insns, None)
        if c is None:
            continue
        cands.append((va, n * 4, c))
        if len(cands) >= limit:
            break
    print(f"generated {len(cands)} candidates")
    parts = []
    for va, sz, c in cands:
        parts.append(f"VA {va:08X}\nSIZE {sz:X}\nCOMP 3.0.1b210\nEND\n{c}---\n")
    open(SPEC, "w").write("".join(parts))
    r = subprocess.run(["python3", HARNESS, SPEC], capture_output=True, text=True)
    if r.stderr.strip():
        print("HARNESS STDERR:", r.stderr[-1500:])
    wins = [l for l in r.stdout.splitlines() if "MATCH" in l and "-> NO" not in l]
    print("\n".join(wins))
    print(f"wins: {len(wins)} / {len(cands)}")


if __name__ == "__main__":
    main()

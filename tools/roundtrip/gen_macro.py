#!/usr/bin/env python3
"""Macro-form generator for the widen family (ee-gcc 2.96 + SDK asm macros).

Scope (v1): functions matching the verified skeletons:
  A)  lui r,0x7000 / sw $zero, K(r)                    -> SP_SW0(K)
  B)  lui r / lw r,C(r) / lb r,D(r) / dsll32 $a0,r,0x18
      / dsra32 $a0,$a0,0x18 / lui r / sw $a0,S(r)      -> SP_SW_W8(S, SP_LB(C,D))
  C)  lui r / lw r,S(r) / (beqz|bnez) r,tgt / nop      -> if (SP_LW(S)) / if (!SP_LW(S))
  D1) lui r / lw r,C(r) / sb $zero,K(r)                -> SP_SB0(C,K)
  D2) addiu $a0,$zero,I / lui r / lw r,C(r) / sb $a0,K(r) -> SP_SB_IMM(C,K,I)
  D3) lui r / lw $a0,C(r) / lb $v1,K($a0) / addiu $v1,$v1,-1
      / sb $v1,K($a0)                                  -> SP_DECB(C,K)
  jr $ra ends; branch target must be inside, code after join continues.

Emits an installer-format spec (COMP ee-gcc2.96) and tests it.
"""
import glob
import os
import re
import subprocess
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import gen_c_family4 as G

ROOT = G.ROOT
img = G.img

MACROS = r'''typedef unsigned int u32;
#define SP_SW0(off) __asm__ volatile("lui $3,0x7000\n\tsw $0," #off "($3)")
#define SP_LW(off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #off "($3)" : "=r"(r)); r; })
#define SP_LB(ch, k) ({ register signed char r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlb $3," #k "($3)" : "=r"(r)); r; })
#define SP_SB0(ch, k) __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tsb $0," #k "($3)")
#define SP_SB_IMM(ch, k, imm) __asm__ volatile("addiu $4,$0," #imm "\n\tlui $3,0x7000\n\tlw $3," #ch "($3)\n\tsb $4," #k "($3)")
#define SP_SW_W8(off, cval) __asm__ volatile("dsll32 $4,%0,0x18\n\tdsra32 $4,$4,0x18\n\tlui $3,0x7000\n\tsw $4," #off "($3)" :: "r"(cval))
#define SP_DECB(ch, k) __asm__ volatile("lui $3,0x7000\n\tlw $4," #ch "($3)\n\tlb $3," #k "($4)\n\taddiu $3,$3,-1\n\tsb $3," #k "($4)")
'''

REJECT = {}


class Bad(Exception):
    pass


def rtoks(i):
    t = G.toks_of(i)
    return t


def reg_of(i, idx):
    return i.op_str.replace(",", " ").split()[idx].lstrip("$")


def memoff(i):
    t = G.toks_of(i)
    return t[1][1]


def skeleton(insns, va, size):
    """Return C statements or raise Bad(reason)."""
    n = len(insns)
    end = va + size
    stmts = []

    def need(k, m):
        if k >= n or insns[k].mnemonic != m:
            raise Bad(f"expect:{m}")
        return insns[k]

    def is_lui7(i):
        return i.mnemonic == "lui" and "0x7000" in i.op_str

    def parse_access(k):
        """D1/D3 statement starting with lui.  Returns (stmt, k_next)."""
        lui = insns[k]
        lw = need(k + 1, "lw")
        # D3: lw $a0,C(r) / lb $v1,K($a0) / addiu $v1,$v1,-1 / sb $v1,K($a0)
        if (lw.op_str.startswith("$a0") and k + 4 < n
                and insns[k + 2].mnemonic == "lb"
                and insns[k + 3].mnemonic == "addiu"
                and " -1" in insns[k + 3].op_str.replace(",", " ,")
                and insns[k + 3].op_str.startswith("$v1")
                and insns[k + 4].mnemonic == "sb"):
            ch = memoff(lw)
            kk = memoff(insns[k + 2])
            koff = memoff(insns[k + 4])
            if kk != koff:
                raise Bad("decb-mismatch")
            return f"SP_DECB(0x{ch:X}, 0x{kk:X})", k + 5
        # D1: lw r,C(r) / sb $zero,K(r)
        if insns[k + 2].mnemonic == "sb" and "$zero" in insns[k + 2].op_str:
            ch = memoff(lw)
            kk = memoff(insns[k + 2])
            return f"SP_SB0(0x{ch:X}, 0x{kk:X})", k + 3
        raise Bad("body-shape")

    def parse_widen_store(k):
        """B: lui / lw r,C(r) / lb r,D(r) / dsll32 / dsra32 / lui / sw $a0,S(r)."""
        lw = need(k + 1, "lw")
        lb = need(k + 2, "lb")
        d1 = need(k + 3, "dsll32")
        d2 = need(k + 4, "dsra32")
        lui2 = need(k + 5, "lui")
        sw = need(k + 6, "sw")
        if "0x18" not in d1.op_str or not is_lui7(lui2) or not sw.op_str.startswith("$a0"):
            raise Bad("widen-shape")
        ch, kk = memoff(lw), memoff(lb)
        return (f"SP_SW_W8(0x{memoff(sw):X}, SP_LB(0x{ch:X}, 0x{kk:X}))", k + 7)

    k = 0
    while True:
        while k < n and insns[k].mnemonic == "nop":
            k += 1
        if k >= n:
            break
        i = insns[k]
        if i.mnemonic == "jr":
            rest = [x for x in insns[k + 1:] if x.mnemonic != "nop"]
            if rest:
                raise Bad("code-after-jr")
            break
        if is_lui7(i):
            nxt = insns[k + 1] if k + 1 < n else None
            if nxt is None:
                raise Bad("trailing-lui")
            if nxt.mnemonic == "sw" and "$zero" in nxt.op_str:
                stmts.append(f"SP_SW0(0x{memoff(nxt):X});")
                k += 2
                continue
            if nxt.mnemonic == "lw":
                third = insns[k + 2] if k + 2 < n else None
                if third is not None and third.mnemonic == "lb":
                    stmt, k2 = parse_widen_store(k)
                    stmts.append(stmt + ";")
                    k = k2
                    continue
                # D1/D3 body statement
                stmt, k2 = parse_access(k)
                stmts.append(stmt + ";")
                k = k2
                continue
            raise Bad("lui-shape")
        if i.mnemonic in ("beqz", "bnez"):
            # condition: previous two must be lui / lw same reg
            if k < 2 or not is_lui7(insns[k - 2]) or insns[k - 1].mnemonic != "lw":
                raise Bad("cond-shape")
            if memoff(insns[k - 1]) != memoff_needed(insns, k, i):
                pass
            S = memoff(insns[k - 1])
            if k + 1 >= n or insns[k + 1].mnemonic != "nop":
                raise Bad("delay-slot")
            tgt = G.branch_target(i)
            if tgt is None or not (va < tgt <= end):
                raise Bad("branch-out")
            if tgt <= i.address:
                raise Bad("backward-branch")
            tidx = next((q for q in range(k + 1, n) if insns[q].address == tgt), None)
            if tidx is None:
                raise Bad("join-miss")
            body = []
            bk = k + 2
            while bk < tidx:
                b = insns[bk]
                if b.mnemonic == "nop":
                    bk += 1
                    continue
                if is_lui7(b):
                    stmt, bk2 = parse_access(bk)
                    body.append(stmt + ";")
                    bk = bk2
                    continue
                if b.mnemonic == "addiu" and b.op_str.startswith("$a0, $zero"):
                    # D2: addiu $a0,$zero,I / lui / lw r,C(r) / sb $a0,K(r)
                    imm = b.op_str.split(",")[2].strip()
                    lui = need(bk + 1, "lui")
                    lw = need(bk + 2, "lw")
                    sb = need(bk + 3, "sb")
                    if not sb.op_str.startswith("$a0"):
                        raise Bad("d2-shape")
                    body.append(f"SP_SB_IMM(0x{memoff(lw):X}, 0x{memoff(sb):X}, {imm});")
                    bk = bk + 4
                    continue
                raise Bad("body-insn:" + b.mnemonic)
            neg = "!" if i.mnemonic == "bnez" else ""
            stmts.append(f"if ({neg}SP_LW(0x{S:X})) {{")
            stmts.extend("    " + s for s in body)
            stmts.append("}")
            k = tidx
            continue
        raise Bad("insn:" + i.mnemonic)
    if not stmts:
        raise Bad("empty")
    return stmts


def memoff_needed(insns, k, br):
    return None


def build_src(va, stmts):
    return MACROS + f"\nvoid func_{va:08X}(void)\n{{\n" + \
        "\n".join("    " + s for s in stmts) + "\n}\n"


def main():
    maxbytes = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    matched = set(l.strip().split(":")[0].split("@")[0]
                  for l in open(f"{ROOT}/src_ro9/matched.txt") if l.strip())
    spec = []
    scanned = 0
    built = 0
    for s in sorted(glob.glob(f"{ROOT}/ro9/func_*.s")):
        stem = os.path.basename(s)[:-2]
        if stem in matched:
            continue
        va, size, insns = G.load_insns(stem)
        if size > maxbytes:
            continue
        if not any(i.mnemonic in G.WIDEN for i in insns):
            continue
        scanned += 1
        if len(insns) < size // 4:
            REJECT["mmi"] = REJECT.get("mmi", 0) + 1
            continue
        try:
            stmts = skeleton(insns, va, size)
            src = build_src(va, stmts)
        except Bad as e:
            REJECT[str(e)] = REJECT.get(str(e), 0) + 1
            continue
        spec.append(f"VA {va:08X}\nSIZE {size:X}\nCOMP ee-gcc2.96\nEND\n{src}---\n")
        built += 1
    print(f"widen-fn scanned {scanned}, skeleton-built {built}")
    print("rejects:", ", ".join(f"{k}={v}" for k, v in
                                sorted(REJECT.items(), key=lambda e: -e[1])[:15]))
    open(f"{ROOT}/pilots/spec_macro.txt", "w").write("".join(spec))
    if not spec:
        return
    r = subprocess.run(["python3", f"{ROOT}/pilots/gcc_try.py",
                        f"{ROOT}/pilots/spec_macro.txt"],
                       capture_output=True, text=True)
    wins = re.findall(r"=== cand \d+: (func_[0-9A-F]{8}).*?-> (MATCH(?:\+PAD)?)", r.stdout)
    uniq = sorted(set(wins))
    print(f"wins: {len(wins)} ({len(uniq)} distinct)")
    for w, v in uniq:
        print(f"WIN {w} {v}")


if __name__ == "__main__":
    main()

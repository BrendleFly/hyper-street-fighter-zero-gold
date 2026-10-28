#!/usr/bin/env python3
"""Branch-focused census of the unmatched ro9 functions.  v2

v2 fixes: capstone renders compares-against-zero as beqz/bnez (separate
mnemonics) and short unconditional jumps as `b` — count them, and record
what instruction produces each branch condition.  Examples are the
SMALLEST functions per family (best for hand-matching).
"""
import glob
import os
import collections

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
IMG_BASE = 0x1F0000
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

COND = {"beq", "bne", "blez", "bgtz", "bltz", "bgez", "beql", "bnel",
        "blezl", "bgtzl", "bltzl", "bgezl", "beqz", "bnez", "beqzl", "bnezl"}
FPU = {"bc1t", "bc1f", "bc1tl", "bc1fl"}


def cond_kind(prev, br):
    p = prev.mnemonic if prev else "?"
    if p in ("slt", "sltu", "slti", "sltiu"):
        return "cmp:" + p
    if p == "andi":
        return "mask:" + br
    if p in ("lw", "lh", "lhu", "lb", "lbu"):
        return "load:" + br
    if p in ("addiu", "addu", "subu"):
        return "arith:" + br
    return p + ":" + br


def matched_set():
    out = set()
    for l in open(f"{ROOT}/src_ro9/matched.txt"):
        l = l.strip()
        if l:
            out.add(l.split(":")[0].split("@")[0])
    return out


def main():
    matched = matched_set()
    fam = collections.Counter()
    br_mn = collections.Counter()
    ckind = collections.Counter()
    delay_nop = 0
    delay_real = 0
    fam_sizes = collections.defaultdict(list)
    fam_calls = collections.Counter()

    for s in sorted(glob.glob(f"{ROOT}/ro9/func_*.s")):
        stem = os.path.basename(s)[:-2]
        if stem in matched:
            continue
        va = int(stem[5:], 16)
        n = sum(1 for l in open(s) if l.strip().startswith(".word"))
        size = n * 4
        off = va - IMG_BASE
        insns = list(md.disasm(img[off:off + size], va))
        if not insns:
            continue
        end = va + size
        stats = dict(ncond=0, nback=0, nfwd=0, nout=0, nswitch=0,
                     nfpu=0, ncall=0, njump=0)
        for i, ins in enumerate(insns):
            m = ins.mnemonic
            if m in COND or m in FPU:
                stats["ncond"] += 1
                br_mn[m] += 1
                toks = ins.op_str.replace(",", " ").split()
                try:
                    tgt = int(toks[-1], 0)
                except ValueError:
                    tgt = None
                if m in FPU:
                    stats["nfpu"] += 1
                if tgt is None or not (va <= tgt < end):
                    stats["nout"] += 1
                elif tgt <= ins.address:
                    stats["nback"] += 1
                else:
                    stats["nfwd"] += 1
                if i + 1 < len(insns):
                    if insns[i + 1].mnemonic == "nop":
                        delay_nop += 1
                    else:
                        delay_real += 1
                ckind[cond_kind(insns[i - 1] if i else None, m)] += 1
            elif m == "jr":
                if "$ra" not in ins.op_str:
                    stats["nswitch"] += 1
            elif m == "jal":
                stats["ncall"] += 1
            elif m in ("j", "b"):
                toks = ins.op_str.split()
                try:
                    tgt = int(toks[0], 0)
                except ValueError:
                    tgt = None
                if tgt is not None and va <= tgt < end:
                    stats["njump"] += 1

        if stats["ncond"] == 0 and stats["nswitch"] == 0:
            continue
        # frame = any stack traffic (sp as base reg), widen = dsll32/dsra32 pair
        framed = any("$sp" in i.op_str for i in insns)
        widen = any(i.mnemonic in ("dsll32", "dsra32", "dsll", "dsra") for i in insns)
        if stats["nswitch"]:
            key = "switch"
        elif stats["nfpu"]:
            key = "fpu"
        elif stats["nback"]:
            key = "loop"
        elif stats["nout"]:
            key = "weird"
        elif stats["nfwd"]:
            key = "fwd%d" % min(stats["nfwd"], 4)
        else:
            key = "jonly"
        key += "/frame" if framed else "/no frame"
        key += "/widen" if widen else ""
        fam[key] += 1
        fam_sizes[key].append((size, stem))
        if stats["ncall"]:
            fam_calls[key] += 1

    tot = sum(fam.values())
    print(f"branchy unmatched functions: {tot}")
    print("\n--- families (n / with-calls) ---")
    for k, v in sorted(fam.items(), key=lambda e: -e[1]):
        sizes = sorted(fam_sizes[k])
        small = " ".join("%s(%dB)" % (st, sz) for sz, st in sizes[:5])
        med = sizes[len(sizes) // 2][0]
        print(f"{v:6d} {fam_calls[k]:6d}  {k:8s} med={med:4d}B  smallest: {small}")
    print("\n--- branch mnemonics ---")
    for k, v in br_mn.most_common(20):
        print(f"{v:6d}  {k}")
    print("\n--- delay slots: nop=%d real=%d ---" % (delay_nop, delay_real))
    print("\n--- condition producer (prev insn : branch) ---")
    for k, v in ckind.most_common(25):
        print(f"{v:6d}  {k}")


if __name__ == "__main__":
    main()

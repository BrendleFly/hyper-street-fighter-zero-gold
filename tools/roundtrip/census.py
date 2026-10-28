#!/usr/bin/env python3
"""Census the unmatched ro9 functions by decoded instruction shape.

Uses capstone on the original image (the split .s files hold raw words only,
no mnemonics, so they cannot be pattern-matched directly).

Prints a shape breakdown so we know which C-generation strategy applies to
which population of functions.
"""
import glob
import os
import re
import sys
import collections

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
IMG_BASE = 0x1F0000
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

SCRATCH_LO = 0x1100
SCRATCH_HI = 0x1200


def matched_set():
    out = set()
    for l in open(f"{ROOT}/src_ro9/matched.txt"):
        l = l.strip()
        if not l:
            continue
        out.add(l.split(":")[0].split("@")[0])
    return out


def decode(stem):
    va = int(stem[5:], 16)
    n = sum(1 for l in open(f"{ROOT}/ro9/{stem}.s") if l.strip().startswith(".word"))
    off = va - IMG_BASE
    body = img[off:off + n * 4]
    return va, n * 4, list(md.disasm(body, va))


def classify(insns):
    """Return (frame_kind, call_kind, op_signature)."""
    frame = "none"
    calls = 0
    jalrs = 0
    for ins in insns:
        m = ins.mnemonic
        op = ins.op_str
        if m in ("sd", "sld") and "$ra" in op and frame == "none":
            frame = "sd"
        if m in ("ld", "ldl") and "$ra" in op and frame == "sd":
            frame = "sd"
        if m == "jal":
            calls += 1
        if m == "jalr":
            jalrs += 1
    sig = collections.Counter()
    for ins in insns:
        sig[ins.mnemonic] += 1
    return frame, calls, jalrs, sig


def main():
    matched = matched_set()
    total = 0
    unmatched = 0
    groups = collections.Counter()
    examples = collections.defaultdict(list)
    for s in sorted(glob.glob(f"{ROOT}/ro9/func_*.s")):
        stem = os.path.basename(s)[:-2]
        total += 1
        if stem in matched:
            continue
        unmatched += 1
        va, size, insns = decode(stem)
        frame, calls, jalrs, sig = classify(insns)
        # scratchpad base usage: lui v,0x7000
        has_base = any(i.mnemonic == "lui" and "0x7000" in i.op_str for i in insns)
        # call target count
        key = (frame, "jal" if calls else ("jalr" if jalrs else "none"), "base" if has_base else "nobase",
               "small" if size <= 96 else ("med" if size <= 160 else "big"))
        groups[key] += 1
        if len(examples[key]) < 4:
            examples[key].append((stem, size, calls, jalrs))

    print(f"total={total} matched={total-unmatched} unmatched={unmatched}")
    print()
    for k, v in sorted(groups.items(), key=lambda e: -e[1]):
        frame, call, base, sz = k
        ex = " ".join(f"{a}({b}B,c{c},r{d})" for a, b, c, d in examples[k])
        print(f"{v:6d}  frame={frame:5s} call={call:5s} {base:5s} {sz:5s}  {ex}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Diagnose why the straight-line decoder rejects functions.

Counts, over all unmatched functions, which instruction caused the decode to
fail, so we know which shapes to add support for.
"""
import collections
import glob
import os
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

# mnemonics the decoder handles
HANDLED = {
    "addiu", "lui", "ori", "xori", "add", "addu", "sub", "and", "or", "xor",
    "nor", "sll", "srl", "sra", "move", "lb", "lbu", "lh", "lhu", "lw",
    "sb", "sh", "sw", "jal", "sd", "ld", "jr", "nop", "dsll", "dsrl", "dsra",
    "dsll32", "dsra32", "sllv", "srlv", "srav", "mult", "div", "mfhi", "mflo",
    "slt", "sltu", "slti", "sltiu", "slti32",
}

UNHANDLED = collections.Counter()
SIZE_BUCKETS = collections.Counter()
TOTAL = 0
BRANCHY = 0
STRAIGHT = 0
examples = collections.defaultdict(list)

for s in sorted(glob.glob(f"{ROOT}/ro9/func_*.s")):
    stem = os.path.basename(s)[:-2]
    va = int(stem[5:], 16)
    n = sum(1 for l in open(s) if l.strip().startswith(".word"))
    size = n * 4
    body = img[va - 0x1F0000: va - 0x1F0000 + size]
    ins = list(md.disasm(body, va))
    TOTAL += 1
    bad = None
    for i in ins:
        if i.mnemonic not in HANDLED:
            bad = i.mnemonic
            break
    if bad:
        UNHANDLED[bad] += 1
        if len(examples[bad]) < 3:
            examples[bad].append(stem)
    else:
        STRAIGHT += 1

print(f"total functions: {TOTAL}")
print(f"no unhandled mnemonic: {STRAIGHT}")
print("\nunhandled mnemonics (count, examples):")
for m, c in UNHANDLED.most_common(40):
    print(f"  {m:12s} {c:6d}   {' '.join(examples[m])}")

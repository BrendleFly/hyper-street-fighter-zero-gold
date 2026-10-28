#!/usr/bin/env python3
"""Dump one ro9 function's disassembly.  Usage: dumpfn.py 0021B450 [more VAs...]"""
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
IMG_BASE = 0x1F0000
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

for arg in sys.argv[1:]:
    va = int(arg, 16)
    n = sum(1 for l in open(f"{ROOT}/ro9/func_{va:08X}.s")
            if l.strip().startswith(".word"))
    off = va - IMG_BASE
    print(f"=== func_{va:08X}  ({n*4} bytes, {n} words) ===")
    for i in md.disasm(img[off:off + n * 4], va):
        print(f"  {i.address:08X}: {i.mnemonic:10s} {i.op_str}")
    print()

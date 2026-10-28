#!/usr/bin/env python3
"""Mirror install_wins2's verify (gcc -S, postprocess, as, ld --defsym,
objcopy) for every spec block of one VA and print word-level diffs.
Usage: blkdiff.py <VAhex>"""
import re
import struct
import subprocess
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import gcc_try
from install_wins2 import undefined_symbols, sym_addr

ROOT = "/home/user/sfzfg/roundtrip"
GCC296 = "/home/user/sfzfg/compilers/ee-gcc2.96/bin/ee-gcc"

va = int(sys.argv[1], 16)
spec = open(f"{ROOT}/pilots/spec_macro2.txt").read()
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
n = 0
for blk in spec.split("---\n"):
    m = re.match(r"VA ([0-9A-F]{8})\nSIZE ([0-9A-F]+)\nCOMP (\S+)\nEND\n(.*)",
                 blk, re.S)
    if not m or int(m.group(1), 16) != va:
        continue
    n += 1
    size = int(m.group(2), 16)
    src = m.group(4)
    open("/tmp/bd.c", "w").write(src)
    subprocess.run([GCC296, "-O1", "-fno-delayed-branch", "-S", "-o", "/tmp/bd.s",
                    "/tmp/bd.c"], capture_output=True, text=True)
    gcc_try.postprocess_s("/tmp/bd.s")
    subprocess.run(["mipsel-linux-gnu-as", "-EL", "-march=r5900", "-mabi=eabi",
                    "-G", "128", "-o", "/tmp/bd.o", "/tmp/bd.s"], capture_output=True)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-R", ".reginfo", "-R",
                    ".MIPS.abiflags", "-R", ".pdr", "-R", ".gnu.attributes",
                    "/tmp/bd.o", "/tmp/bd.o"], check=False)
    defs = []
    for s in undefined_symbols("/tmp/bd.o"):
        defs += ["--defsym", f"{s}=0x{sym_addr(s):x}"]
    open("/tmp/bd.ld", "w").write(
        f"SECTIONS {{ . = 0x{va:08X}; .text : {{ /tmp/bd.o(.text) }} }}\n")
    subprocess.run(["mipsel-linux-gnu-ld", "-T", "/tmp/bd.ld", "-o", "/tmp/bd.elf"] + defs,
                   capture_output=True, text=True)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "/tmp/bd.elf",
                    "/tmp/bd.bin"], check=False)
    got = open("/tmp/bd.bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
    if got == tgt:
        print(f"--- block {n}: MATCH ({len(got)}B)")
        continue
    nd = sum(1 for a, b in zip(got, tgt) if a != b)
    print(f"--- block {n}: {nd} bytes differ, got {len(got)}B vs {size}B")
    words = sorted(set((i & ~3) for i in range(min(len(got), len(tgt)))
                       if got[i] != tgt[i]))
    for w in words[:14]:
        print(f"  @{va + w:08X}: got {struct.unpack('<I', got[w:w+4])[0]:08X}"
              f"  want {struct.unpack('<I', tgt[w:w+4])[0]:08X}")
if n == 0:
    print("no blocks for that VA")

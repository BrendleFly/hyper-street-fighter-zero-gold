#!/usr/bin/env python3
"""Full linked diff of macro-spec candidates vs target."""
import re
import subprocess
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
G296 = "/home/user/sfzfg/compilers/ee-gcc2.96/bin/ee-gcc"
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
img = open(f"{ROOT}/ro9_original.bin", "rb").read()

spec = open(f"{ROOT}/pilots/spec_macro2.txt").read()
blocks = [b for b in spec.split("---\n") if b.strip()]
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 2
shown = 0
for b in blocks:
    va = int(re.search(r"VA ([0-9A-F]+)", b).group(1), 16)
    size = int(re.search(r"SIZE ([0-9A-F]+)", b).group(1), 16)
    src = b.split("END\n", 1)[1]
    open("/tmp/dbg.c", "w").write(src)
    r = subprocess.run([G296, "-O1", "-fno-delayed-branch", "-S", "-o", "/tmp/dbg.s", "/tmp/dbg.c"],
                       capture_output=True, text=True)
    if r.returncode:
        print(f"=== {va:08X}: EEGCC FAIL: {r.stderr[-200:]}")
        continue
    r = subprocess.run(["mipsel-linux-gnu-as", "-EL", "-march=r5900", "-mabi=eabi",
                        "-G", "128", "-o", "/tmp/dbg.o", "/tmp/dbg.s"],
                       capture_output=True, text=True)
    open("/tmp/dbg.ld", "w").write(
        f"SECTIONS {{ . = 0x{va:08X}; .text : {{ /tmp/dbg.o(.text) }} }}\n")
    nm = subprocess.run(["mipsel-linux-gnu-nm", "-u", "/tmp/dbg.o"],
                        capture_output=True, text=True).stdout
    defs = []
    for line in nm.splitlines():
        p = line.split()
        if p and p[-1].startswith("func_"):
            defs += ["--defsym", f"{p[-1]}=0x{int(p[-1][5:], 16):x}"]
    subprocess.run(["mipsel-linux-gnu-ld", "-T", "/tmp/dbg.ld", "-o", "/tmp/dbg.elf"] + defs,
                   capture_output=True)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text",
                    "/tmp/dbg.elf", "/tmp/dbg.bin"], capture_output=True)
    got = open("/tmp/dbg.bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
    gl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(got, va)]
    tl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(tgt, va)]
    shown += 1
    print(f"=== {va:08X} got {len(got)}B vs {size}B")
    for k in range(max(len(gl), len(tl))):
        g = gl[k] if k < len(gl) else "-"
        t = tl[k] if k < len(tl) else "-"
        print((" " if g == t else "*") + f" {g:36s} | {t}")
    print()
    if shown >= limit:
        break

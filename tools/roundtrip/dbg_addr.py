#!/usr/bin/env python3
"""Addressed disasm diff for ONE spec_macro2 candidate block.

Usage: python3 dbg_addr.py 0026EEE0 [block_index]
Rebuilds the Nth spec block for the VA through the exact install pipeline
(ee-gcc -O1 -S + postprocess + gas + defsym link), then prints both the
built and original disassembly WITH addresses, aligned, '*' on diffs.
"""
import re
import subprocess
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
G296 = "/home/user/sfzfg/compilers/ee-gcc2.96/bin/ee-gcc"
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
img = open(f"{ROOT}/ro9_original.bin", "rb").read()

va_arg = sys.argv[1].replace("func_", "")
va = int(va_arg, 16)
which = int(sys.argv[2]) if len(sys.argv) > 2 else 0
spec_path = sys.argv[3] if len(sys.argv) > 3 else f"{ROOT}/pilots/spec_macro2.txt"

blocks = [b for b in open(spec_path).read().split("---\n")
          if b.strip() and int(re.search(r"VA ([0-9A-F]+)", b).group(1), 16) == va]
print(f"{len(blocks)} block(s) for {va:08X}; using #{which}")
b = blocks[which]
src = b.split("END\n", 1)[1]
open("/tmp/ga.c", "w").write(src)

r = subprocess.run([G296, "-O1", "-fno-delayed-branch"] + sys.argv[4:] +
                   ["-S", "-o", "/tmp/ga.s", "/tmp/ga.c"],
                   capture_output=True, text=True)
if r.returncode:
    print("COMPILE FAIL:")
    print(r.stderr[:2000])
    sys.exit(1)


def postprocess(path):
    lines = open(path).read().split("\n")
    out = []
    for ln in lines:
        s = ln.strip()
        if s == ".set reorder":
            out.append("\t.set\tnoreorder")
            continue
        out.append(ln)
        w = s.replace("\t", " ").split(" ")[0] if s else ""
        if w in ("jal", "j", "jr", "beq", "bne", "blez", "bgtz", "bltz",
                 "bgez", "beqz", "bnez", "b") and not s.endswith(":"):
            out.append("\tnop")
    txt = "\n".join(out)
    if ".set\tnoreorder" not in txt.split("#APP")[0]:
        txt = txt.replace("\t.text", "\t.text\n\t.set noreorder", 1)
    txt = re.sub(r"subu\t(\$sp,\$sp,)(\d+)",
                 lambda m: "addiu\t%s-%d" % (m.group(1), int(m.group(2))), txt)
    txt = txt.replace("addu\t$sp,$sp,", "addiu\t$sp,$sp,")
    open(path, "w").write(txt)


postprocess("/tmp/ga.s")
subprocess.run(["mipsel-linux-gnu-as", "-EL", "-march=r5900", "-mabi=eabi",
                "-G", "128", "-o", "/tmp/ga.o", "/tmp/ga.s"], capture_output=True)
nm = subprocess.run(["mipsel-linux-gnu-nm", "-u", "/tmp/ga.o"],
                    capture_output=True, text=True).stdout
defs = []
for line in nm.splitlines():
    p = line.split()
    if p and p[-1].startswith("func_"):
        defs += ["--defsym", f"{p[-1]}=0x{int(p[-1][5:], 16):x}"]
open("/tmp/ga.ld", "w").write(
    f"SECTIONS {{ . = 0x{va:08X}; .text : {{ /tmp/ga.o(.text) }} }}\n")
r = subprocess.run(["mipsel-linux-gnu-ld", "-T", "/tmp/ga.ld", "-o", "/tmp/ga.elf"] + defs,
                   capture_output=True, text=True)
if r.returncode:
    print("LINK FAIL: " + r.stderr[:400])
    sys.exit(1)
subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary",
                "--only-section=.text", "/tmp/ga.elf", "/tmp/ga.bin"],
               capture_output=True)
got = open("/tmp/ga.bin", "rb").read()
size = 4 * sum(1 for l in open(f"{ROOT}/ro9/func_{va:08X}.s")
               if l.strip().startswith(".word"))
tgt = img[va - 0x1F0000: va - 0x1F0000 + size]

gl = [(f"{i.address:08X} {i.mnemonic} {i.op_str}") for i in md.disasm(got, va)]
tl = [(f"{i.address:08X} {i.mnemonic} {i.op_str}") for i in md.disasm(tgt, va)]
bad = 0
for k in range(max(len(gl), len(tl))):
    g = gl[k] if k < len(gl) else "-"
    t = tl[k] if k < len(tl) else "-"
    mark = " " if g == t else "*"
    if g != t:
        bad += 1
    print(f"{mark} {g:44s} | {t}")
print(f"\n{bad} bad insns; built .s kept at /tmp/ga.s")

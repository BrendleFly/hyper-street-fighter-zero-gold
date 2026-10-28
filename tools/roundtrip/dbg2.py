#!/usr/bin/env python3
"""Debug macro-spec candidates with the exact install pipeline (postprocess
+ defsyms), skipping already-matched stems.  Args: [max_show] [max_bad_bytes]"""
import re
import subprocess
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
G296 = "/home/user/sfzfg/compilers/ee-gcc2.96/bin/ee-gcc"
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
matched = set(l.strip().split(":")[0].split("@")[0]
              for l in open(f"{ROOT}/src_ro9/matched.txt") if l.strip())


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
        txt = txt.replace("\t.text", "\t.text\n\t.set\tnoreorder", 1)
    txt = re.sub(r"subu\t(\$sp,\$sp,)(\d+)",
                 lambda m: "addiu\t%s-%d" % (m.group(1), int(m.group(2))), txt)
    txt = txt.replace("addu\t$sp,$sp,", "addiu\t$sp,$sp,")
    open(path, "w").write(txt)


max_show = int(sys.argv[1]) if len(sys.argv) > 1 else 3
max_bad = int(sys.argv[2]) if len(sys.argv) > 2 else 8
shown = 0
for b in open(f"{ROOT}/pilots/spec_macro2.txt").read().split("---\n"):
    if not b.strip():
        continue
    va = int(re.search(r"VA ([0-9A-F]+)", b).group(1), 16)
    if f"func_{va:08X}" in matched:
        continue
    src = b.split("END\n", 1)[1]
    open("/tmp/g2.c", "w").write(src)
    r = subprocess.run([G296, "-O1", "-fno-delayed-branch", "-S",
                        "-o", "/tmp/g2.s", "/tmp/g2.c"], capture_output=True, text=True)
    if r.returncode:
        print(f"... {va:08X} COMPILE FAIL: {r.stderr[-80:]}")
        continue
    postprocess("/tmp/g2.s")
    subprocess.run(["mipsel-linux-gnu-as", "-EL", "-march=r5900", "-mabi=eabi",
                    "-G", "128", "-o", "/tmp/g2.o", "/tmp/g2.s"], capture_output=True)
    nm = subprocess.run(["mipsel-linux-gnu-nm", "-u", "/tmp/g2.o"],
                        capture_output=True, text=True).stdout
    defs = []
    for line in nm.splitlines():
        p = line.split()
        if p and p[-1].startswith("func_"):
            defs += ["--defsym", f"{p[-1]}=0x{int(p[-1][5:], 16):x}"]
    open("/tmp/g2.ld", "w").write(
        f"SECTIONS {{ . = 0x{va:08X}; .text : {{ /tmp/g2.o(.text) }} }}\n")
    r = subprocess.run(["mipsel-linux-gnu-ld", "-T", "/tmp/g2.ld", "-o", "/tmp/g2.elf"] + defs,
                       capture_output=True, text=True)
    if r.returncode:
        print(f"... {va:08X} LINK FAIL: {r.stderr[-80:]}")
        continue
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary",
                    "--only-section=.text", "/tmp/g2.elf", "/tmp/g2.bin"],
                   capture_output=True)
    got = open("/tmp/g2.bin", "rb").read()
    size = 4 * sum(1 for l in open(f"{ROOT}/ro9/func_{va:08X}.s")
                   if l.strip().startswith(".word"))
    tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
    gl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(got, va)]
    tl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(tgt, va)]
    bad = sum(1 for k in range(max(len(gl), len(tl)))
              if (gl[k] if k < len(gl) else "-") != (tl[k] if k < len(tl) else "-"))
    if bad * 4 <= max_bad and shown < max_show:
        shown += 1
        print(f"=== {va:08X} got {len(got)}B vs {size}B, {bad} bad insns")
        for k in range(max(len(gl), len(tl))):
            g = gl[k] if k < len(gl) else "-"
            t = tl[k] if k < len(tl) else "-"
            print((" " if g == t else "*") + f" {g:36s} | {t}")
        print()
    if shown >= max_show:
        break

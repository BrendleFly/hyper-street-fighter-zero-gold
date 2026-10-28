#!/usr/bin/env python3
"""Raw-ize mnemonic instruction lines in a splat .s file using original image bytes.

Rabbitizer emits some EE (MMI) byte patterns as MIPS32r2/DSP lookalike mnemonics
(`ext`, `dps.w.ph`, ...) that GNU as cannot or should not re-encode. The image
bytes are authoritative, so failing lines are replaced by .word directives.
"""
import re, struct, sys

IMG = r"C:\Users\user\Documents\ZCode\PS2_Decomp\SFZFG Decomp Project\baserom\mwo3_dec\ro9.bin"
LOAD = 0x1F0000

def rawize(path, region_end=None):
    img = open(IMG, "rb").read()
    src = open(path).read().splitlines()
    label = None
    out = []
    va = None
    rawized = kept = 0
    for line in src:
        m = re.match(r"\s*(?:\.glabel\s+|\.func_)(\w+)", line) or re.match(r"\s*(\w+):", line)
        if label is None and m:
            name = m.group(1)
            am = re.search(r"([0-9A-Fa-f]{8})", name)
            if am:
                label = name
                va = int(am.group(1), 16)
        if re.match(r"^\s+[a-z]", line):  # mnemonic instruction line
            w = struct.unpack_from("<I", img, va - LOAD)[0]
            out.append(f"    .word {w:#010x}        # {va:#x} (raw-ized)")
            va += 4
            rawized += 1
        else:
            if line.startswith(".glabel"):
                out.append(".globl " + line.split(None, 1)[1])
            elif line.startswith(".end"):
                continue
            else:
                out.append(line)
            if re.match(r"^\s+\.word", line):
                va += 4
            kept += 1
    open(path, "w").write("\n".join(out) + "\n")
    print(f"{path}: raw-ized {rawized} mnemonics, kept {kept} lines")

if __name__ == "__main__":
    rawize(sys.argv[1])

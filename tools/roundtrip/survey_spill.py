#!/usr/bin/env python3
"""Survey the "spilled parameter" function family in ro9.

Pattern: a framed function that stores $a0 into its own frame and reloads it
before each use, e.g.

    addiu $sp,$sp,-0x20 / sd $ra,($sp) / sw $a0,0x10($sp) / lw $v1,0x10($sp) / ...

MWCC produces this shape for a *volatile pointer*.  This script counts how
many unmatched functions have the shape and which stack slot offsets the
original uses, so we know whether one layout dominates.
"""
import collections
import glob
import os
import re
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
IMG_BASE = 0x1F0000
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)


def matched_set():
    out = set()
    for l in open(f"{ROOT}/src_ro9/matched.txt"):
        l = l.strip()
        if l:
            out.add(l.split(":")[0].split("@")[0])
    return out


def main():
    matched = matched_set()
    slots = collections.Counter()
    frames = collections.Counter()
    examples = collections.defaultdict(list)
    total = 0
    for s in sorted(glob.glob(f"{ROOT}/ro9/func_*.s")):
        stem = os.path.basename(s)[:-2]
        if stem in matched:
            continue
        va = int(stem[5:], 16)
        n = sum(1 for l in open(s) if l.strip().startswith(".word"))
        off = va - IMG_BASE
        ins = list(md.disasm(img[off:off + n * 4], va))
        txt = [f"{i.mnemonic} {i.op_str}" for i in ins]
        if not txt:
            continue
        # frame prologue
        m = re.match(r"addiu \$sp, \$sp, -(0x[0-9a-f]+)", txt[0])
        if not m:
            continue
        fsize = int(m.group(1), 16)
        # find sw $a0, off($sp)
        sw = None
        for i, t in enumerate(txt[:6]):
            mm = re.match(r"sw \$a0, (0x[0-9a-f]+)\(\$sp\)", t)
            if mm:
                sw = int(mm.group(1), 16)
                break
        if sw is None:
            continue
        # count reloads of that slot
        reloads = sum(1 for t in txt if re.match(r"lw \$v[01], (0x[0-9a-f]+)\(\$sp\)", t)
                      and int(re.match(r"lw \$v[01], (0x[0-9a-f]+)\(\$sp\)", t).group(1), 16) == sw)
        if reloads < 2:
            continue
        total += 1
        slots[sw] += 1
        frames[fsize] += 1
        if len(examples[sw]) < 6:
            examples[sw].append(stem)
    print(f"unmatched spilled-parameter functions: {total}")
    print("\nslot offset -> count   (examples)")
    for k, v in sorted(slots.items()):
        print(f"  0x{k:02x}($sp)  {v:5d}   {' '.join(examples[k])}")
    print("\nframe size -> count")
    for k, v in sorted(frames.items()):
        print(f"  0x{k:02x}  {v:5d}")


if __name__ == "__main__":
    main()

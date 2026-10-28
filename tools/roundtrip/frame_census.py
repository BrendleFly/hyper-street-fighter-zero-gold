#!/usr/bin/env python3
"""Census the framed unmatched functions by frame geometry.

For every unmatched function whose $sp traffic is MORE than the simple call
frame, record: frame size, presence of sd $ra, the entry param stores
(sw $aN, off($sp)) with their offsets, and the stride between them.
The stride tells us which compiler produced it: MWCC packs volatile-param
homes 4 bytes apart; the original ro9 style is 0x10/0x20/0x30 (16-stride).
"""
import collections
import glob
import os
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import gen_c_family4 as G

matched = set(l.strip().split(":")[0].split("@")[0]
              for l in open(f"{G.ROOT}/src_ro9/matched.txt") if l.strip())
pat = collections.Counter()
examples = collections.defaultdict(list)

for s in sorted(glob.glob(f"{G.ROOT}/ro9/func_*.s")):
    stem = os.path.basename(s)[:-2]
    if stem in matched:
        continue
    va, size, insns = G.load_insns(stem)
    if size > 1536:
        continue
    if any(i.mnemonic in G.WIDEN for i in insns):
        continue
    if not any("$sp" in i.op_str for i in insns):
        continue
    if G.strip_call_frame(insns) is not None:
        continue                       # simple call frame, already handled
    # frame size from the first addiu sp, sp, -K
    frame = None
    for i in insns:
        if i.mnemonic == "addiu" and "$sp, $sp, -" in i.op_str.replace("  ", " "):
            t = i.op_str.replace(" ", "").split(",")
            try:
                frame = -int(t[2], 0)
            except ValueError:
                pass
            break
    sd_ra = any(i.mnemonic == "sd" and "$ra" in i.op_str for i in insns[:6])
    # entry param stores: sw $aN, off($sp) within the first 8 instructions
    homes = []
    for i in insns[:8]:
        if i.mnemonic == "sw" and "($sp)" in i.op_str:
            toks = i.op_str.replace(",", " ").split()
            if toks[0] in ("$a0", "$a1", "$a2", "$a3"):
                off = toks[1].replace("($sp)", "")
                try:
                    homes.append((int(toks[0][2]), int(off, 0)))
                except ValueError:
                    pass
    homes.sort()
    if len(homes) >= 2:
        offs = [h[1] for h in homes]
        strides = {offs[k + 1] - offs[k] for k in range(len(offs) - 1)}
        if strides == {4}:
            kind = "stride4"
        elif strides == {8}:
            kind = "stride8"
        elif strides == {16}:
            kind = "stride16"
        else:
            kind = "mixed"
    elif len(homes) == 1:
        kind = "one-home@0x%X" % homes[0][1]
    else:
        kind = "no-param-stores"
    key = (kind, "sd-ra" if sd_ra else "no-sd", frame)
    pat[key] += 1
    if len(examples[key]) < 3:
        examples[key].append(stem)

print("framed unmatched (no widen, <=1536B, not simple call frame):")
for (kind, sd, frame), n in sorted(pat.items(), key=lambda e: -e[1])[:20]:
    print(f"{n:5d}  {kind:14s} {sd:6s} frame=0x{frame:X}   {' '.join(examples[(kind, sd, frame)])}")

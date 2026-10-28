#!/usr/bin/env python3
"""How many unmatched functions contain MMI instructions that capstone's
MIPS64 mode cannot decode (disasm stops early)?

MMI opcodes (dpa.w.ph, madd, pivetc) belong to the PS2 EE's Multimedia
Instruction set; capstone has no EE support, so md.disasm silently stops at
the first one.  Functions affected cannot be decoded (let alone generated)
without an MMI-aware disassembler.
"""
import glob
import os
import struct
import sys
import collections

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import gen_c_family4 as G

matched = set(l.strip().split(":")[0].split("@")[0]
              for l in open(f"{G.ROOT}/src_ro9/matched.txt") if l.strip())

# MMI major opcode bits (from the EE user manual): SPECIAL2 (011000) MMIs
def is_mmi_word(w):
    op = (w >> 26) & 0x3F
    if op == 0x1C:                      # SPECIAL2: most MMI alu ops
        return True
    if op == 0x1F:                      # MMI table jumps / etc? conservative
        return False
    return False

groups = collections.Counter()
tot = collections.Counter()
for s in sorted(glob.glob(f"{G.ROOT}/ro9/func_*.s")):
    stem = os.path.basename(s)[:-2]
    if stem in matched:
        continue
    va, size, insns = G.load_insns(stem)
    nwords = size // 4
    stopped = len(insns) < nwords
    # widen?
    widen = any(i.mnemonic in G.WIDEN for i in insns)
    key = ("widen" if widen else "nowiden",
           "capstone-stops" if stopped else "decodes")
    tot[key] += 1

print(f"{'family':30s} count")
for k, v in sorted(tot.items()):
    print(f"{str(k):30s} {v}")

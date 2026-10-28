#!/usr/bin/env python3
"""Diagnose store-cold-val: print stems + disassembly of a few functions
whose structure() decode fails with that reason.  Read-only, no compiling."""
import sys
sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import glob
import os

import gen_c_family4 as G

matched = set(l.strip().split(":")[0].split("@")[0]
              for l in open(f"{G.ROOT}/src_ro9/matched.txt") if l.strip())
shown = 0
reasons = {}
for s in sorted(glob.glob(f"{G.ROOT}/ro9/func_*.s")):
    stem = os.path.basename(s)[:-2]
    if stem in matched:
        continue
    va, size, insns = G.load_insns(stem)
    if size > 1536:
        continue
    if any(i.mnemonic in G.WIDEN for i in insns):
        continue
    if any("$sp" in i.op_str for i in insns):
        if G.strip_call_frame(insns) is None:
            continue
        insns = G.strip_call_frame(insns)
    try:
        G.structure(insns, va, size)
    except G.Stop as e:
        reasons[str(e)] = reasons.get(str(e), 0) + 1
        if str(e) == "store-cold-val" and shown < 3:
            shown += 1
            print(f"--- {stem} ({size}B) ---")
            for i in insns:
                print(f"  {i.address:08X}: {i.mnemonic:10s} {i.op_str}")
            print()
print("reasons:", sorted(reasons.items(), key=lambda kv: -kv[1])[:12])

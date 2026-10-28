#!/usr/bin/env python3
"""Dump a few functions rejected with else-join-miss, showing branch/j
structure so the shape can be diagnosed."""
import sys
sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import glob
import os

import gen_c_family4 as G

matched = set(l.strip().split(":")[0].split("@")[0]
              for l in open(f"{G.ROOT}/src_ro9/matched.txt") if l.strip())
shown = 0
for s in sorted(glob.glob(f"{G.ROOT}/ro9/func_*.s")):
    stem = os.path.basename(s)[:-2]
    if stem in matched:
        continue
    va, size, insns = G.load_insns(stem)
    if size > 1536:
        continue
    if any(i.mnemonic in G.WIDEN for i in insns):
        continue
    if len(insns) < size // 4:
        continue                       # capstone-stops (MMI)
    if any("$sp" in i.op_str for i in insns):
        if G.strip_call_frame(insns) is None:
            continue
        insns = G.strip_call_frame(insns)
    try:
        G.structure(insns, va, size)
    except G.Stop as e:
        if str(e) == "else-join-miss" and shown < 3:
            shown += 1
            print(f"--- {stem} ({size}B) ---")
            for i in insns:
                m = i.mnemonic
                if m in G.BRANCH_OPS or m in ("j", "b", "jr") or "$sp" in i.op_str:
                    print(f"  {i.address:08X}: {m:8s} {i.op_str}")
                else:
                    print(f"  {i.address:08X}: {m}")
            print()
    if shown >= 3:
        break

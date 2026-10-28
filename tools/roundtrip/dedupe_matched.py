#!/usr/bin/env python3
"""Collapse duplicate stems in src_ro9/matched.txt (keep the first entry).

A function must appear exactly once: it is compiled once and linked once.
Keeps the file sorted by stem.
"""
import sys

MT = "/home/user/sfzfg/roundtrip/src_ro9/matched.txt"

lines = [l.strip() for l in open(MT) if l.strip()]
seen = set()
out = []
dups = []
for l in lines:
    stem = l.split(":")[0].split("@")[0]
    if stem in seen:
        dups.append(l)
        continue
    seen.add(stem)
    out.append(l)
out = sorted(out, key=lambda x: x.split(":")[0].split("@")[0])
open(MT, "w").write("\n".join(out) + "\n")
print(f"removed {len(dups)} duplicate entries; matched.txt now {len(out)} entries")
if dups:
    print("  removed:", " ".join(dups))

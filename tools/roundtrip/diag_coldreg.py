#!/usr/bin/env python3
"""Cold-source census at the generator's REAL raise sites: decode_run's env
is replaced by a dict subclass that logs every .get() miss, tagged with the
instruction being processed (captured via a patched toks_of).
Args: [max_show]"""
import collections
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_c_family4 as G

max_show = int(sys.argv[1]) if len(sys.argv) > 1 else 3

CUR = (None, None)          # (mnemonic, op_str) of the instruction at hand
MISSES = set()              # (func, addr, mnem, reg)


class ColdDict(dict):
    def get(self, k, default=None):
        if k is not None and not isinstance(k, int) and dict.get(self, k, None) is None:
            if default is None or default == ("?",):
                MISSES.add((STEM, CUR[0], CUR[1], k))
        return dict.get(self, k, default)

    def __getitem__(self, k):
        if k not in self and k is not None and not isinstance(k, int):
            MISSES.add((STEM, CUR[1], CUR[0], k))
        return dict.__getitem__(self, k)


orig_toks = G.toks_of


def toks_of(ins):
    CUR = (ins.address, ins.mnemonic)
    globals()["CUR"] = CUR
    return orig_toks(ins)


G.toks_of = toks_of

orig_run = G.decode_run


def wrapped_run(insns, env=None, nc=None):
    env = ColdDict(env) if env is not None else ColdDict()
    return orig_run(insns, env, nc)


G.decode_run = wrapped_run

MATCHED = set(l.strip().split(":")[0].split("@")[0]
              for l in open(f"{G.ROOT}/src_ro9/matched.txt") if l.strip())
STEM = None
for s in sorted(glob.glob(f"{G.ROOT}/ro9/func_*.s")):
    stem = os.path.basename(s)[:-2]
    if stem in MATCHED:
        continue
    STEM = stem
    try:
        va, size, insns = G.load_insns(stem)
    except FileNotFoundError:
        continue
    if size > 1536:
        continue
    if any(i.mnemonic in G.WIDEN for i in insns):
        continue
    if len(insns) < size // 4:
        continue
    if any("$sp" in i.op_str for i in insns):
        st = G.strip_call_frame(insns)
        if st is None:
            continue
        insns = st
    try:
        G.structure(insns, va, size)
    except G.Stop:
        pass

agg = collections.Counter()
prod = collections.Counter()
bysite = {}
for func, addr, mnem, reg in MISSES:
    agg[f"{mnem}:{reg}"] += 1
    bysite.setdefault(f"{mnem}:{reg}", []).append((func, addr))
print("=== env .get() misses by (insn:reg) ===")
for k, v in agg.most_common(24):
    print(f"{v:5d}  {k}   e.g. {bysite[k][:max_show]}")

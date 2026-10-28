#!/usr/bin/env python3
"""Census frame shapes of the unmatched non-widen pool (<=1536B) whose stack
traffic strip_call_frame rejects.  For each: frame size K, saved-register
set, and every sp-relative access OUTSIDE the standard prologue/epilogue,
grouped so the generator's frame model can target the dominant shape."""
import collections
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_c_family4 as G

matched = set(l.strip().split(":")[0].split("@")[0]
              for l in open(f"{G.ROOT}/src_ro9/matched.txt") if l.strip())
shapes = collections.Counter()
extra_kinds = collections.Counter()
examples = {}


def frame_shape(insns):
    """Parse the standard prologue/epilogue; return (K, saved, extra list)."""
    K = None
    saved = []
    pro = 0                       # prologue insn count
    i = 0
    # addiu sp,sp,-K   (or sd ra first then addiu — accept both orders)
    while i < len(insns):
        m = insns[i].mnemonic
        t = G.toks_of(insns[i])
        if m == "addiu" and G.rname(t[0][1]) == "$sp" and G.rname(t[1][1]) == "$sp":
            K = -G.s16(int(t[2][1], 0))
            pro += 1
            i += 1
            break
        if m == "sd" and "$ra" in t[0][1] + t[1][1] and "$sp" in t[1][1]:
            saved.append("ra")
            pro += 1
            i += 1
            continue
        if m == "sd" and "$sp" in t[1][1]:
            r = t[0][1]
            mm = re.match(r"^\$(s[0-7]|fp|gp)$", r)
            if not mm:
                return None
            saved.append(r[1:])
            pro += 1
            i += 1
            continue
        if m in ("sd", "sw") and ("$gp" in t[1][1] or "$fp" in t[1][1]):
            pro += 1
            i += 1
            continue
        break
    if K is None:
        return None
    # scan the body for sp traffic that is not part of the standard frame
    extra = []
    body = insns[pro:]
    for ins in body:
        m = ins.mnemonic
        t = G.toks_of(ins)
        if m in ("sd", "sw") and "$ra" in t[0][1] + t[1][1] and "$sp" in t[1][1]:
            continue
        if m in ("ld", "lw") and "$ra" in t[0][1] + t[1][1] and "$sp" in t[1][1]:
            continue
        if m in ("ld", "lw") and "$sp" in t[1][1]:
            r = t[0][1]
            if re.match(r"^\$(s[0-7]|fp|gp|ra)$", r):
                continue
            extra.append(("ld:" + r, ins.address, t[1][1]))
        elif m in ("sd", "sw", "sb", "sh") and "$sp" in t[1][1]:
            r = t[0][1]
            mm = re.match(r"^\$(s[0-7]|fp|gp|ra)$", r)
            if mm and m == "sd":
                continue
            extra.append((m + ":" + r, ins.address, t[1][1]))
        elif m == "addiu" and G.rname(t[0][1]) == "$sp" and G.rname(t[1][1]) == "$sp":
            if G.s16(int(t[2][1], 0)) > 0:
                continue                       # epilogue restore
            extra.append(("sub-sp", ins.address, t[2][1]))
    return (K, tuple(saved), extra)


for s in sorted(glob.glob(f"{G.ROOT}/ro9/func_*.s")):
    stem = os.path.basename(s)[:-2]
    if stem in matched:
        continue
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
    if "$sp" not in " ".join(i.op_str for i in insns):
        continue
    st = G.strip_call_frame(insns)
    if st is not None:
        shapes["standard-frame(strip-ok)"] += 1
        continue
    fs = frame_shape(insns)
    if fs is None:
        shapes["unparsed-prologue"] += 1
        examples.setdefault("unparsed-prologue", []).append(stem)
        continue
    K, saved, extra = fs
    key = f"K={K} saved={'+'.join(saved) or '-'} extra={len(extra)}"
    shapes[key] += 1
    if extra:
        for kind, addr, off in extra:
            extra_kinds[f"{kind} {off}"] += 1
    examples.setdefault(key, []).append(stem)

print("=== frame shapes (unmatched non-widen <=1536B, strip-rejected) ===")
for k, v in shapes.most_common(30):
    print(f"{v:5d}  {k}   e.g. {examples.get(k, [])[:3]}")
print("=== extra sp-traffic kinds ===")
for k, v in extra_kinds.most_common(24):
    print(f"{v:5d}  {k}")

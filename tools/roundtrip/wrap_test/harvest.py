#!/usr/bin/env python3
"""Tier-1 harvest: find unmatched functions that are pure v1-based scratchpad
zero-store sequences and auto-generate + byte-test recipe-1 C for them."""
import struct, hashlib, glob, re, os, subprocess
from collections import defaultdict

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
ROOT = "/home/user/sfzfg/roundtrip"
SRC = f"{ROOT}/src_ro9"
BUILD = f"{ROOT}/build_eabi"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()

matched = set(l.strip().split(":")[0] for l in open(f"{SRC}/matched.txt") if l.strip())
funcs = []
for p in glob.glob(f"{ROOT}/ro9/func_*.s"):
    va = int(re.search(r"func_([0-9A-Fa-f]{8})", os.path.basename(p)).group(1), 16)
    n = sum(1 for l in open(p) if re.match(r"\s+\.word", l))
    funcs.append((va, n * 4))
groups = defaultdict(list)
for va, sz in funcs:
    groups[hashlib.md5(img[va - 0x1F0000: va - 0x1F0000 + sz]).hexdigest()].append((va, sz))

def decode_clear_ops(body):
    """Return list of (width, offset) for pure zero-store sequences, else None."""
    ops = []
    i = 0
    n = len(body)
    while i < n:
        w = struct.unpack_from("<I", body, i)[0]
        op = w >> 26
        if w == 0x3c037000:          # lui v1, 0x7000
            i += 4
            continue
        if w == 0x03e00008 or w == 0:  # jr ra / nop
            i += 4
            continue
        rs = (w >> 21) & 31
        rt = (w >> 16) & 31
        if op in (0x2b, 0x28, 0x29) and rs == 3 and rt == 0:  # sw/sb/sh zero, off(v1)
            imm = w & 0xFFFF
            if imm >= 0x8000:
                imm -= 0x10000
            ops.append(({0x2b: 4, 0x28: 1, 0x29: 2}[op], imm))
            i += 4
            continue
        return None
    if not ops:
        return None
    return ops

def gen_c(name, ops):
    lines = ["typedef unsigned int u32;", "", f"void func_{name}(void)", "{", "    u32 a;", ""]
    for width, off in ops:
        a = 0x70000000
        lines.append(f"    a = 0x70000000;")
        t = {4: "u32", 1: "u8", 2: "u16"}[width]
        lines.append(f"    *(volatile {t} *)(a + {off:#x}) = 0;")
        lines.append("")
    lines.append("}")
    return "\n".join(lines) + "\n"

def compile_test(va, c_text):
    open(f"{SRC}/func_{va:08X}.c", "w").write(c_text)
    o = f"/tmp/hv_{va:08X}.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"{SRC}/func_{va:08X}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        return None
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    return open("/tmp/g.bin", "rb").read()

candidates = 0
results = []
seen_group = set()
for va, sz in funcs:
    stem = f"func_{va:08X}"
    if stem in matched:
        continue
    body = img[va - 0x1F0000: va - 0x1F0000 + sz]
    ops = decode_clear_ops(body)
    if ops is None:
        continue
    key = hashlib.md5(body).hexdigest()
    if key in seen_group:
        continue
    seen_group.add(key)
    candidates += 1
    members = groups[key]
    got = compile_test(va, gen_c(f"{va:08X}", ops))
    if got is None:
        results.append((len(members), va, "compile-fail", 0))
        continue
    tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]
    if got == tgt:
        pad = 0
        verdict = "MATCH"
    elif len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
        pad = len(tgt) - len(got)
        verdict = f"MATCH+pad{pad}"
    else:
        results.append((len(members), va, "no", 0))
        continue
    total = 0
    for mva, msz in members:
        stem = f"func_{mva:08X}"
        open(f"{SRC}/{stem}.c", "w").write(gen_c(f"{mva:08X}", ops))
        oo = f"{BUILD}/{stem}.o"
        subprocess.run([WIBO, MW] + CFLAGS + ["-o", oo, f"{SRC}/{stem}.c"], capture_output=True, text=True)
        subprocess.run(["mipsel-linux-gnu-objcopy", "--set-section-alignment", ".text=4", oo, oo + ".t"], check=True)
        os.replace(oo + ".t", oo)
        if pad:
            subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", oo, "/tmp/t.bin"], check=False)
            body2 = open("/tmp/t.bin", "rb").read() + bytes(pad)
            open("/tmp/padded.bin", "wb").write(body2)
            subprocess.run(["mipsel-linux-gnu-objcopy", "--update-section", ".text=/tmp/padded.bin", oo, oo + ".p"], check=True)
            os.replace(oo + ".p", oo)
        total += 1
    results.append((len(members), va, verdict, total))

print(f"clear-sequence groups found: {candidates}")
wins = 0
for cnt, va, verdict, total in results:
    if verdict.startswith("MATCH"):
        wins += total
        print(f"  x{cnt} @{va:#x}: {verdict}")
print(f"functions newly matched: {wins}")
print(f"failed groups: {[(c, hex(v)) for c, v, r, _ in results if r in ('no', 'compile-fail')][:10]}")

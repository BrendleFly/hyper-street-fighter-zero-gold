#!/usr/bin/env python3
"""Byte-level diff for the closest spec_macro2 rejects: for each of the N
distinct functions with fewest differing bytes, print the VA and raw words
at every differing offset, plus ±1 instruction context.
Usage: diff_survey2.py [N] [max_bytes]"""
import re
import struct
import subprocess
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import gcc_try

ROOT = "/home/user/sfzfg/roundtrip"
GCC296 = "/home/user/sfzfg/compilers/ee-gcc2.96/bin/ee-gcc"

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
MAXBYTES = int(sys.argv[2]) if len(sys.argv) > 2 else 60

r = subprocess.run(["python3", f"{ROOT}/pilots/install_wins2.py",
                    f"{ROOT}/pilots/spec_macro2.txt"],
                   capture_output=True, text=True)
rows = re.findall(r"REJECT (func_[0-9A-F]{8}) \[(\S+)\]: (\d+) bytes differ", r.stdout)
best = {}
for full, comp, nb in rows:
    b = int(nb)
    if full not in best or b < best[full][0]:
        best[full] = (b, comp)
picks = sorted(((v[0], k, v[1]) for k, v in best.items() if v[0] <= MAXBYTES))[:N]
print(f"{len(rows)} reject rows, {len(best)} distinct; showing {len(picks)}")

spec = open(f"{ROOT}/pilots/spec_macro2.txt").read()
for nb, full, comp in picks:
    va = int(full[5:], 16)
    src = size = None
    for blk in spec.split("---\n"):
        m = re.match(r"VA ([0-9A-F]{8})\nSIZE ([0-9A-F]+)\nCOMP (\S+)\nEND\n(.*)",
                     blk, re.S)
        if m and m.group(1) == full[5:] and m.group(3) == comp:
            src, size = m.group(4), int(m.group(2), 16)
            break
    if src is None:
        continue
    open("/tmp/ds.c", "w").write(src)
    subprocess.run([GCC296, "-O1", "-fno-delayed-branch", "-S", "-o", "/tmp/ds.s",
                    "/tmp/ds.c"], capture_output=True, text=True)
    gcc_try.postprocess_s("/tmp/ds.s")
    subprocess.run(["mipsel-linux-gnu-as", "-EL", "-march=r5900", "-mabi=eabi",
                    "-G", "128", "-o", "/tmp/ds.o", "/tmp/ds.s"], capture_output=True)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary",
                    "--only-section=.text", "/tmp/ds.o", "/tmp/ds.bin"],
                   capture_output=True)
    got = open("/tmp/ds.bin", "rb").read()
    tgt = img_slice = open(f"{ROOT}/ro9_original.bin", "rb").read()[
        va - 0x1F0000: va - 0x1F0000 + size]
    print(f"=== {full} [{comp}] {nb} bytes differ, got {len(got)}B vs {size}B")
    offs = sorted(set(i for i in range(min(len(got), len(tgt)))
                      if got[i] != tgt[i]))
    # group into word offsets
    words = sorted(set(o & ~3 for o in offs))
    for w in words:
        go = struct.unpack("<I", got[w:w + 4])[0]
        to = struct.unpack("<I", tgt[w:w + 4])[0]
        print(f"  @{va + w:08X}: got {go:08X}  want {to:08X}")

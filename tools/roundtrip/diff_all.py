#!/usr/bin/env python3
"""Print the side-by-side diff of one C candidate against the original, for
every installed mwccps2 build, so the closest build can be identified.

Usage: python3 diff_all.py <va_hex> <cfile> [optflags]
"""
import os
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import ccdis

CDIR = "/home/user/sfzfg/compilers"


def main():
    va = int(sys.argv[1], 16)
    src = open(sys.argv[2]).read()
    opt = sys.argv[3].split(",") if len(sys.argv) > 3 else ["-O1"]
    comps = []
    for d in sorted(os.listdir(CDIR)):
        exe = f"{CDIR}/{d}/mwccps2.exe"
        if d.startswith("mwcps2-") and os.path.exists(exe):
            comps.append((d[len("mwcps2-"):], exe))
    for name, exe in comps:
        got, err = ccdis.build(src, name, opt, "da")
        if got is None:
            print(f"===== {name}: COMPILE FAIL")
            continue
        tgt = ccdis.img[va - 0x1F0000: va - 0x1F0000 + len(got)]
        gl = ccdis.dis(got, va)
        tl = ccdis.dis(tgt, va)
        n = sum(1 for a, b in zip(got, tgt) if a != b)
        nd = sum(1 for g, t in zip(gl, tl) if g != t)
        print(f"===== {name}: {n} bytes differ, {nd} instructions differ, got {len(got)}B")
        for i in range(max(len(gl), len(tl))):
            g = gl[i] if i < len(gl) else "-"
            t = tl[i] if i < len(tl) else "-"
            if g != t:
                print(f"    * {g:<42} | {t}")


if __name__ == "__main__":
    main()

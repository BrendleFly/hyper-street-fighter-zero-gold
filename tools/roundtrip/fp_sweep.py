#!/usr/bin/env python3
"""Sweep every mwccps2 build on the constant-function-pointer call form.

The original binary calls a fixed function through a computed address:
    lui   $v0, 0x4b
    addiu $v0, $v0, -0x6920
    jalr  $v0
which is a call to 0x4A96E0.  MWCC folds a constant function pointer into a
direct `jal` in some builds - those cannot match.  This finds the builds
that do NOT fold, and shows how each one materialises the constant.

Usage: python3 fp_sweep.py
"""
import os
import re
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import ccdis

CDIR = "/home/user/sfzfg/compilers"

SRC = """
typedef unsigned int u32;
void f(void)
{
    ((void (*)(void))0x4A96E0)();
}
"""

SRC2 = """
typedef unsigned int u32;
extern void func_004A96E0();
void f(void)
{
    ((void (*)(void))func_004A96E0)();
}
"""


def main():
    comps = []
    for d in sorted(os.listdir(CDIR)):
        exe = f"{CDIR}/{d}/mwccps2.exe"
        if d.startswith("mwcps2-") and os.path.exists(exe):
            comps.append((d[len("mwcps2-"):], exe))
    for label, src in (("CONSTANT 0x4A96E0", SRC), ("EXTERN symbol", SRC2)):
        print(f"########## {label}")
        for name, exe in comps:
            got, err = ccdis.build(src, name, ["-O1"], "fps")
            if got is None:
                print(f"  {name:22s} COMPILE FAIL")
                continue
            lines = ccdis.dis(got, 0)
            body = [l.split(":", 1)[1].strip() for l in lines]
            # keep the interesting middle part (skip prologue/epilogue)
            inner = [b for b in body if not b.startswith(("addiu $sp", "sd", "ld", "jr", "nop", "xori", "ext"))]
            kind = "JALR" if any("jalr" in b for b in inner) else ("JAL" if any("jal " in b for b in inner) else "?")
            lui = [b for b in inner if b.startswith("lui")]
            addu = [b for b in inner if b.startswith("addiu")]
            print(f"  {name:22s} {kind:5s} {' ; '.join(lui + addu)}")


if __name__ == "__main__":
    main()

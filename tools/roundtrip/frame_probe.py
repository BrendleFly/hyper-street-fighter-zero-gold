#!/usr/bin/env python3
"""Probe mwccps2's frame layout so we can place locals at the offsets the
original binary uses.

Prints, for each source variant: the frame size, and every sp-relative
offset that appears (stores and loads), so we can deduce the rule.
"""
import subprocess
import os
import re
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
from ccdis import build, dis

VARIANTS = {
    "A_1param_volatile_local": """
extern void callee();
void f(signed char *p)
{
    signed char * volatile q = p;
    q[1] = 0;
    q[2] = 0;
    q[6] = 0;
    callee();
}
""",
    "B_1param_volatile_local_2nd": """
extern void callee();
void f(signed char *p)
{
    int z;
    signed char * volatile q = p;
    z = 1;
    q[1] = 0;
    q[2] = 0;
    q[6] = 0;
    callee();
}
""",
    "C_1param_normal_local": """
extern void callee();
void f(signed char *p)
{
    int z = 1;
    z = z + 1;
    p[1] = 0;
    p[2] = 0;
    p[6] = 0;
    callee();
}
""",
    "D_1param_volatile_param": """
extern void callee();
void f(signed char * volatile p)
{
    p[1] = 0;
    p[2] = 0;
    p[6] = 0;
    callee();
}
""",
    "E_2params": """
extern void callee();
void f(signed char *p, signed char *r)
{
    signed char * volatile q = p;
    q[1] = 0;
    r[2] = 0;
    callee();
}
""",
    "F_1param_call_with_arg": """
extern void callee(signed char *);
void f(signed char *p)
{
    signed char * volatile q = p;
    q[1] = 0;
    q[2] = 0;
    q[6] = 0;
    callee(p);
}
""",
    "G_1param_volatile_local_2locals": """
extern void callee();
void f(signed char *p)
{
    int z;
    int w;
    signed char * volatile q = p;
    z = 1; w = 2;
    q[1] = 0;
    q[2] = 0;
    q[6] = 0;
    callee();
}
""",
    "H_1param_volatile_local_after_call": """
extern void callee();
void f(signed char *p)
{
    signed char * volatile q = p;
    q[1] = 0;
    callee();
    q[2] = 0;
    q[6] = 0;
}
""",
}


def main():
    comp = sys.argv[1] if len(sys.argv) > 1 else "3.0.1b210"
    opt = sys.argv[2].split(",") if len(sys.argv) > 2 else ["-O1"]
    for name, src in VARIANTS.items():
        got, err = build(src, comp, opt, "fp")
        if got is None:
            print(f"{name}: COMPILE FAIL {(err or '')[-300:]}")
            continue
        lines = dis(got, 0)
        frame = "?"
        offs = []
        for l in lines:
            m = re.search(r"addiu \$sp, \$sp, -(0x[0-9a-f]+)", l)
            if m:
                frame = m.group(1)
            for mm in re.finditer(r"\$sp\)\s*$", l):
                pass
            mo = re.search(r"(-?0x[0-9a-f]+)\(\$sp\)", l)
            if mo:
                offs.append((mo.group(1), l.split(" ", 2)[-1].strip()))
        print(f"{name}: frame={frame}")
        for o, ins in offs:
            print(f"      {o:>8}  {ins}")


if __name__ == "__main__":
    main()

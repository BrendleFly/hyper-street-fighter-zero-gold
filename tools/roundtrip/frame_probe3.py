#!/usr/bin/env python3
"""Confirm MWCC's local-area allocation direction (up from base vs down from top).

Emits N volatile locals and prints the frame offsets they receive.
"""
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
from ccdis import build, dis


def src_for(n):
    decls = "\n".join(f"    signed char * volatile v{i};" for i in range(n))
    inits = " ".join(f"v{i} = 0;" for i in range(n))
    return f"""
extern void callee();
void f(void)
{{
{decls}
    {inits}
    callee();
}}
"""


def main():
    comp = sys.argv[1] if len(sys.argv) > 1 else "3.0.1b210"
    for n in (1, 2, 3, 4, 5, 6):
        got, err = build(src_for(n), comp, ["-O1"], "fp3")
        if got is None:
            print(f"n={n}: COMPILE FAIL {(err or '')[-200:]}")
            continue
        offs = []
        frame = "?"
        for l in dis(got, 0):
            parts = l.split()
            if "addiu" in l and "-0x" in l and "$sp, $sp" in l:
                frame = l.split("-0x")[1].split()[0]
            if "$sp)" in l and ("sw" in l or "lw" in l):
                o = l.split("(")[-1].split(")")[0]
                offs.append((o, parts[-3] if len(parts) > 3 else ""))
        print(f"n={n}  comp={comp}  frame=0x{frame}  offsets={[o for o,_ in offs]}")


if __name__ == "__main__":
    main()

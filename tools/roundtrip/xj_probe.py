#!/usr/bin/env python3
"""Print structure_local's segs tree for one function (cross-jump debugging).
Usage: python3 xj_probe.py 0026EEE0
"""
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import gen_c_family4 as G          # noqa: E402
import gen_macro2 as M             # noqa: E402


def show(segs, ind=1):
    for seg in segs:
        if seg[0] == "acts":
            for a in seg[1]:
                if a[0] == "mstmt":
                    print("    " * ind + a[1])
        else:
            node = seg if isinstance(seg, list) else list(seg)
            _, cond, then_s, else_s = node[:4]
            print("    " * ind + f"IF cond={cond}")
            show(then_s, ind + 1)
            if else_s is None:
                print("    " * (ind + 1) + "(no else)")
            elif else_s and else_s[0][0] == "xgoto":
                print("    " * (ind + 1) + f"ELSE -> goto {else_s[0][1]}")
            else:
                print("    " * (ind + 1) + "ELSE:")
                show(else_s, ind + 2)


def main():
    arg = sys.argv[1].strip()
    stem = arg if arg.startswith("func_") else "func_" + arg.upper()
    va, size, insns = G.load_insns(stem)
    print(f"loaded {stem}: size={size} bytes")
    stripped = G.strip_call_frame(insns)
    if stripped is None:
        print("REJECT: frame")
        return
    print(f"stripped: {len(stripped)} insns")
    G.decode_run = M.macro_decode_run
    G.extract_cond = M.macro_extract_cond
    M.CTX = M.Ctx("$2")
    try:
        segs, alias = M.structure_local(stripped, va, size)
    except G.Stop as e:
        print(f"STOP: {e}")
        return
    print("--- segs tree ---")
    show(segs)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Find where mwccps2 puts the argument home slot for an incoming pointer arg
that must survive a call, and where it puts volatile locals.

Usage: python3 frame_probe4.py [compiler]
"""
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
from ccdis import build, dis

CASES = {
    "param_used_after_call": """
extern void callee();
void f(signed char *p)
{
    callee();
    p[1] = 0;
}
""",
    "param_used_before_and_after_call": """
extern void callee();
void f(signed char *p)
{
    p[1] = 0;
    callee();
    p[2] = 0;
}
""",
    "param_passed_as_arg": """
extern void callee(signed char *);
void f(signed char *p)
{
    callee(p);
}
""",
    "param_passed_as_arg_and_used": """
extern void callee(signed char *);
void f(signed char *p)
{
    callee(p);
    p[2] = 0;
}
""",
    "two_params_one_used_after_call": """
extern void callee();
void f(signed char *p, signed char *r)
{
    callee();
    p[1] = 0;
}
""",
    "volatile_local_only": """
extern void callee();
void f(void)
{
    signed char * volatile q = 0;
    q[1] = 0;
    callee();
}
""",
}


def main():
    comp = sys.argv[1] if len(sys.argv) > 1 else "3.0.1b210"
    for name, src in CASES.items():
        got, err = build(src, comp, ["-O1"], "fp4")
        print(f"===== {name}  [{comp}]")
        if got is None:
            print("  COMPILE FAIL", (err or "")[-300:])
            continue
        for l in dis(got, 0):
            print("   ", l)


if __name__ == "__main__":
    main()

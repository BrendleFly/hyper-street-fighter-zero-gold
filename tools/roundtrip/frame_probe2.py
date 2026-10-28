#!/usr/bin/env python3
"""Print full disassembly for frame-layout probe variants."""
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
from ccdis import build, dis

V = {
    "one_volatile_local": """
extern void callee();
void f(void)
{
    signed char * volatile q;
    q = 0;
    callee();
}
""",
    "three_volatile_locals": """
extern void callee();
void f(void)
{
    signed char * volatile q;
    signed char * volatile r;
    signed char * volatile s;
    q = 0; r = 0; s = 0;
    callee();
}
""",
    "two_params_volatile_local": """
extern void callee();
void f(signed char *p, signed char *r)
{
    signed char * volatile q = p;
    q[1] = 0;
    r[2] = 0;
    callee();
}
""",
    "one_param_call_with_arg": """
extern void callee(signed char *);
void f(signed char *p)
{
    p[1] = 0;
    callee(p);
}
""",
    "one_param_call_with_2args": """
extern void callee(signed char *, int);
void f(signed char *p)
{
    p[1] = 0;
    callee(p, 3);
}
""",
    "one_param_volatile_local_call_arg": """
extern void callee(signed char *);
void f(signed char *p)
{
    signed char * volatile q = p;
    q[1] = 0;
    callee(p);
}
""",
}


def main():
    comp = sys.argv[1] if len(sys.argv) > 1 else "3.0.1b210"
    for name, src in V.items():
        got, err = build(src, comp, ["-O1"], "fp2")
        print(f"===== {name}  (comp {comp})")
        if got is None:
            print("  COMPILE FAIL", (err or "")[-300:])
            continue
        for l in dis(got, 0):
            print("   ", l)


if __name__ == "__main__":
    main()

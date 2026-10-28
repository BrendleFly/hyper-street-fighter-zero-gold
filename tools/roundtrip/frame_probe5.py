#!/usr/bin/env python3
"""Find C constructs that make mwccps2 place a 32-bit value at sp+0x10 in a
0x20 frame - the offset the original binary uses for the parameter it
repeatedly reloads.

Each case is compiled and its disassembly printed so the slot offsets can be
compared against the target shape:

    addiu $sp,$sp,-0x20 / sd $ra,($sp) / sw $a0,0x10($sp) / lw $v1,0x10($sp) ...
"""
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
from ccdis import build, dis

CASES = {
    "addr_of_param_taken": """
extern void callee();
void f(signed char *p)
{
    signed char **pp = &p;
    *pp = p;
    callee();
}
""",
    "param_is_uint_volatile_local": """
extern void callee();
void f(unsigned int p)
{
    volatile unsigned int q = p;
    q = q + 1;
    callee();
}
""",
    "uint_param_volatile_local_cast": """
extern void callee();
void f(unsigned int p)
{
    volatile unsigned int q = p;
    *(volatile unsigned char *)(q + 1) = 0;
    *(volatile unsigned char *)(q + 2) = 0;
    *(volatile unsigned char *)(q + 6) = 0;
    callee();
}
""",
    "uint_param_volatile_local_nocast": """
extern void callee();
void f(unsigned int p)
{
    volatile unsigned int q = p;
    q = 0;
    callee();
}
""",
    "uint_param_plain": """
extern void callee();
void f(unsigned int p)
{
    *(volatile unsigned char *)(p + 1) = 0;
    *(volatile unsigned char *)(p + 2) = 0;
    *(volatile unsigned char *)(p + 6) = 0;
    callee();
}
""",
    "volatile_local_8byte": """
extern void callee();
void f(void)
{
    volatile long long q = 0;
    q = q + 1;
    callee();
}
""",
    "volatile_local_two_words": """
extern void callee();
void f(void)
{
    volatile unsigned int q = 0;
    volatile unsigned int r = 0;
    q = 0; r = 0;
    callee();
}
""",
    "volatile_local_4byte_after_int_local": """
extern void callee();
void f(void)
{
    int z;
    volatile unsigned int q;
    z = 1;
    q = 0;
    callee();
}
""",
}


def main():
    comp = sys.argv[1] if len(sys.argv) > 1 else "3.0.1b210"
    for name, src in CASES.items():
        got, err = build(src, comp, ["-O1"], "fp5")
        print(f"===== {name}  [{comp}]")
        if got is None:
            print("  COMPILE FAIL", (err or "")[-400:])
            continue
        for l in dis(got, 0):
            print("   ", l)


if __name__ == "__main__":
    main()

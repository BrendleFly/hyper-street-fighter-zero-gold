#!/usr/bin/env python3
"""Generate candidate C variants for scratchpad-pointer style functions and
test them all on build-box. Emits a tryc.py spec file."""
import subprocess, itertools, os, sys

HARNESS = "/home/user/sfzfg/roundtrip/pilots/tryc.py"
SPEC = "/home/user/sfzfg/roundtrip/pilots/spec_gen.txt"

# family: func -> (va, size, list of (label, c_source))
FAMILIES = {}

# --- func_002514D0: store u16 -0xeef to (0xbb0000 - 0x3d64) ---
FAMILIES["func_002514D0"] = (0x002514D0, 8, [
    ("value-first",
     """typedef unsigned short u16;
typedef unsigned int u32;
void func_002514D0(void)
{
    u32 v = -0xeef;
    u32 base = 0xbb0000;
    *(volatile u16 *)(base - 0x3d64) = v;
}
"""),
    ("value-first-u16var",
     """typedef unsigned short u16;
typedef unsigned int u32;
void func_002514D0(void)
{
    u16 v = -0xeef;
    u32 base = 0xbb0000;
    *(volatile u16 *)(base - 0x3d64) = v;
}
"""),
    ("value-first-order2",
     """typedef unsigned short u16;
typedef unsigned int u32;
void func_002514D0(void)
{
    u32 base = 0xbb0000;
    u16 v = -0xeef;
    *(volatile u16 *)(base - 0x3d64) = v;
}
"""),
    ("store-to-ptr",
     """typedef unsigned short u16;
typedef unsigned int u32;
void func_002514D0(void)
{
    u16 v = -0xeef;
    volatile u16 *p = (volatile u16 *)(0xbb0000 - 0x3d64);
    *p = v;
}
"""),
    ("direct-value-neg",
     """typedef unsigned short u16;
typedef unsigned int u32;
void func_002514D0(void)
{
    u16 v = -0xeef;
    volatile u16 *p = (volatile u16 *)0xbb0000;
    *(p - 0x3d64) = v;
}
"""),
])

# --- func_00420F00: xor-1 a byte at (ptr from 0x70001118) + 0xb ---
FAMILIES["func_00420F00"] = (0x00420F00, 16, [
    ("ptr-var-volatile",
     """typedef unsigned char u8;
typedef unsigned int u32;
void func_00420F00(void)
{
    volatile u8 *p = (volatile u8 *)(*(volatile u32 *)(0x70001118));
    *(volatile u8 *)(p + 0xb) ^= 1;
}
"""),
    ("ptr-var-plain",
     """typedef unsigned char u8;
typedef unsigned int u32;
void func_00420F00(void)
{
    u8 *p = (u8 *)(*(volatile u32 *)(0x70001118));
    *(volatile u8 *)(p + 0xb) ^= 1;
}
"""),
    ("u32-ptr-var",
     """typedef unsigned char u8;
typedef unsigned int u32;
void func_00420F00(void)
{
    u32 *p = (u32 *)(*(volatile u32 *)(0x70001118));
    *(volatile u8 *)(p + 0xb) ^= 1;
}
"""),
    ("explicit-temp",
     """typedef unsigned char u8;
typedef unsigned int u32;
void func_00420F00(void)
{
    u32 *p;
    u8 v;
    p = (u32 *)(*(volatile u32 *)(0x70001118));
    v = *(volatile u8 *)(p + 0xb);
    *(volatile u8 *)(p + 0xb) = v ^ 1;
}
"""),
    ("value-first",
     """typedef unsigned char u8;
typedef unsigned int u32;
void func_00420F00(void)
{
    u32 *p;
    u8 v;
    p = (u32 *)(*(volatile u32 *)(0x70001118));
    v = *(volatile u8 *)(p + 0xb);
    v = v ^ 1;
    *(volatile u8 *)(p + 0xb) = v;
}
"""),
    ("no-cast-u32ptr",
     """typedef unsigned char u8;
typedef unsigned int u32;
void func_00420F00(void)
{
    volatile u32 *pp = (volatile u32 *)(0x70001118);
    u8 v = *(volatile u8 *)(*pp + 0xb);
    *(volatile u8 *)(*pp + 0xb) = v ^ 1;
}
"""),
])

# --- func_0028EF40: byte |= 0xff80 at (ptr from 0x70001118) + 0xb4 ---
FAMILIES["func_0028EF40"] = (0x0028EF40, 12, [
    ("or-ff80",
     """typedef unsigned char u8;
typedef unsigned int u32;
void func_0028EF40(void)
{
    u32 *p = (u32 *)(*(volatile u32 *)(0x70001118));
    *(volatile u8 *)(p + 0xb4) |= 0xff80;
}
"""),
    ("or-ff80-var",
     """typedef unsigned char u8;
typedef unsigned int u32;
void func_0028EF40(void)
{
    u32 *p = (u32 *)(*(volatile u32 *)(0x70001118));
    u8 v = *(volatile u8 *)(p + 0xb4);
    *(volatile u8 *)(p + 0xb4) = v | 0xff80;
}
"""),
    ("or-neg80",
     """typedef unsigned char u8;
typedef unsigned int u32;
void func_0028EF40(void)
{
    u32 *p = (u32 *)(*(volatile u32 *)(0x70001118));
    u8 v = *(volatile u8 *)(p + 0xb4);
    *(volatile u8 *)(p + 0xb4) = v | 0xff80;
}
"""),
    ("or-ff80-u8ptr",
     """typedef unsigned char u8;
typedef unsigned int u32;
void func_0028EF40(void)
{
    u8 *p = (u8 *)(*(volatile u32 *)(0x70001118));
    *(volatile u8 *)(p + 0xb4) |= 0xff80;
}
"""),
])

# --- func_0021CA00: s8 load from (0xb7000 - 0x7b94) ---
FAMILIES["func_0021CA00"] = (0x0021CA00, 8, [
    ("base-var",
     """typedef signed char s8;
typedef unsigned int u32;
s8 func_0021CA00(void)
{
    u32 base = 0xb7000;
    return *(volatile s8 *)(base - 0x7b94);
}
"""),
    ("ptr-base",
     """typedef signed char s8;
typedef unsigned int u32;
s8 func_0021CA00(void)
{
    volatile s8 *p = (volatile s8 *)0xb7000;
    return *(volatile s8 *)(p - 0x7b94);
}
"""),
    ("base-var-cast",
     """typedef signed char s8;
typedef unsigned int u32;
s8 func_0021CA00(void)
{
    u32 base = 0xb7000;
    return *(volatile s8 *)((u32)base - 0x7b94);
}
"""),
    ("int-base",
     """typedef signed char s8;
typedef unsigned int u32;
s8 func_0021CA00(void)
{
    int base = 0xb7000;
    return *(volatile s8 *)(base - 0x7b94);
}
"""),
])


def main():
    parts = []
    for name, (va, size, variants) in FAMILIES.items():
        for label, src in variants:
            parts.append(f"VA {va:08X}\nSIZE {size}\nEND\n{src}\n---\n")
    open(SPEC, "w").write("".join(parts))
    r = subprocess.run(["python3", HARNESS, SPEC], capture_output=True, text=True)
    print(r.stdout)
    if r.stderr:
        print("STDERR:", r.stderr[:2000])


if __name__ == "__main__":
    main()

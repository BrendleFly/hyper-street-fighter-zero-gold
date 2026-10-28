#!/usr/bin/env python3
"""Finer sweep: find what makes MWCC emit the char->int sign-extension pair."""
import subprocess

SPEC = "/home/user/sfzfg/roundtrip/pilots/spec_gen.txt"
HARNESS = "/home/user/sfzfg/roundtrip/pilots/tryc.py"
TARGETS = [(0x004AB5F0, "30", 4), (0x0036A1E0, "30", 8), (0x00420DE0, "30", 4)]

V = {
"G": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    s8 v;
    int r;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    v = *(volatile s8 *)(a + 0x370);
    r = v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r & {mask};
}}
""",
"H": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    int r;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    r = *(volatile s8 *)(a + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r & {mask};
}}
""",
"I": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    long r;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    r = *(volatile s8 *)(a + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r & {mask};
}}
""",
"J": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    s8 v;
    int r;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    v = *(volatile s8 *)(a + 0x370);
    r = v & {mask};
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r;
}}
""",
"K": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    u8 v;
    int r;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    v = *(volatile u8 *)(a + 0x370);
    r = v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r & {mask};
}}
""",
"L": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    s8 v;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    v = *(volatile s8 *)(a + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = (u32)(s32)v & {mask};
}}
""",
"M": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    int r;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    r = (int)*(volatile s8 *)(a + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r & {mask};
}}
""",
"N": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    s8 v;
    int r;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    v = *(volatile s8 *)(a + 0x370);
    r = (int)v;
    r &= {mask};
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r;
}}
""",
}

parts = []
for va, size, mask in TARGETS:
    for tag, tpl in V.items():
        parts.append(f"VA {va:08X}\nSIZE {size}\nEND\n" + tpl.format(name=f"{va:08X}", mask=mask) + "---\n")
open(SPEC, "w").write("".join(parts))
r = subprocess.run(["python3", HARNESS, SPEC], capture_output=True, text=True)
lines = [l for l in r.stdout.splitlines() if l.startswith("===")]
print("\n".join(lines))
for l in r.stdout.splitlines():
    if "MATCH" in l and "-> NO" not in l:
        print(l)
if r.stderr:
    print("ERR:", r.stderr[:800])

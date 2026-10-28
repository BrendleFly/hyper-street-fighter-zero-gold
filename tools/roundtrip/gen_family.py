#!/usr/bin/env python3
"""Generate + test variant sweeps for the byte-flag family."""
import subprocess, itertools

SPEC = "/home/user/sfzfg/roundtrip/pilots/spec_gen.txt"
HARNESS = "/home/user/sfzfg/roundtrip/pilots/tryc.py"

# (va, size_hex, mask)
TARGETS = [(0x004AB5F0, "30", 4), (0x0036A1E0, "30", 8), (0x00420DE0, "30", 4)]

VARIANTS = {
    # A: chain var holds pointer, int temp holds value
    "A": """typedef signed char s8;
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
    # B: same but mask applied to r first
    "B": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    int r;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    r = *(volatile s8 *)(a + 0x370);
    r &= {mask};
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r;
}}
""",
    # C: separate pointer var, chain base
    "C": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    s8 *p;
    int r;

    a = 0x70000000;
    p = (s8 *)(*(volatile u32 *)(a + 0x1118));
    r = *(volatile s8 *)(p + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r & {mask};
}}
""",
    # D: value in s8 var, mask in int temp
    "D": """typedef signed char s8;
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
    # E: u32 var reused for value, sign-extended
    "E": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    int r;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    a = *(volatile s8 *)(a + 0x370);
    r = a & {mask};
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r;
}}
""",
    # F: mask on the u32 holding sign-extended byte
    "F": """typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;
    int r;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    a = *(volatile s8 *)(a + 0x370);
    r = a & {mask};
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r;
}}
""",
}

parts = []
for va, size, mask in TARGETS:
    for tag, tpl in VARIANTS.items():
        src = tpl.format(name=f"{va:08X}", mask=mask)
        parts.append(f"VA {va:08X}\nSIZE {size}\nEND\n{src}\n---\n")

open(SPEC, "w").write("".join(parts))
r = subprocess.run(["python3", HARNESS, SPEC], capture_output=True, text=True)
print(r.stdout)
if r.stderr:
    print("ERR:", r.stderr[:1500])

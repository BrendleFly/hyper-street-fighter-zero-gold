#!/usr/bin/env python3
"""Generate a big sweep of pointer-materialization candidates for func_001F4710."""
import os

ROOT = "/home/user/sfzfg/roundtrip"
TYPEDEFS = "typedef unsigned char u8;\ntypedef unsigned short u16;\ntypedef unsigned int u32;\ntypedef signed char s8;\ntypedef signed short s16;\ntypedef signed int s32;\n"

# Each candidate: (name, src)
cands = []

def add(name, src):
    cands.append((name, src))

# Base forms with absolute load
forms = [
    # (decl chain, decl v1, decl q, qexpr, access)
    ("u32 v1; u32 q; v1=*(u32*)0x70001018; q=v1+32; *(s8*)q=...",
     "u32 v1;\nu32 q;\nv1 = *(volatile u32 *)0x70001018;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("u32 q; u32 v1; ...",
     "u32 q;\nu32 v1;\nv1 = *(volatile u32 *)0x70001018;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("volatile u32 v1; u32 q; ...",
     "volatile u32 v1;\nu32 q;\nv1 = *(volatile u32 *)0x70001018;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("u32 v1; volatile u32 q; ...",
     "u32 v1;\nvolatile u32 q;\nv1 = *(volatile u32 *)0x70001018;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("volatile u32 v1; volatile u32 q; ...",
     "volatile u32 v1;\nvolatile u32 q;\nv1 = *(volatile u32 *)0x70001018;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("register u32 v1; u32 q; ...",
     "register u32 v1;\nu32 q;\nv1 = *(volatile u32 *)0x70001018;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("u32 v1; register u32 q; ...",
     "u32 v1;\nregister u32 q;\nv1 = *(volatile u32 *)0x70001018;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("register u32 v1; register u32 q; ...",
     "register u32 v1;\nregister u32 q;\nv1 = *(volatile u32 *)0x70001018;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
]

# separate `chain` var forms
chain_forms = [
    ("u32 chain; u32 v1; u32 q; chain=load; v1=chain; q=v1+32",
     "u32 chain;\nu32 v1;\nu32 q;\nchain = *(volatile u32 *)0x70001018;\nv1 = chain;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("volatile u32 chain; u32 v1; u32 q; ...",
     "volatile u32 chain;\nu32 v1;\nu32 q;\nchain = *(volatile u32 *)0x70001018;\nv1 = chain;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("u32 chain; u32 v1; volatile u32 q; ...",
     "u32 chain;\nu32 v1;\nvolatile u32 q;\nchain = *(volatile u32 *)0x70001018;\nv1 = chain;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("volatile u32 chain; u32 v1; volatile u32 q; ...",
     "volatile u32 chain;\nu32 v1;\nvolatile u32 q;\nchain = *(volatile u32 *)0x70001018;\nv1 = chain;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("u32 chain; u32 v1; register u32 q; ...",
     "u32 chain;\nu32 v1;\nregister u32 q;\nchain = *(volatile u32 *)0x70001018;\nv1 = chain;\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
]

# scaled pointer forms
scaled_forms = [
    ("u32 v1; u32 *q; q=(u32*)v1+8",
     "u32 v1;\nu32 *q;\nv1 = *(volatile u32 *)0x70001018;\nq = (u32 *)v1 + 8;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("u32 v1; u8 *q; q=(u8*)v1+32",
     "u32 v1;\nu8 *q;\nv1 = *(volatile u32 *)0x70001018;\nq = (u8 *)v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("u32 v1; volatile u32 *q; q=(volatile u32*)(v1+32)",
     "u32 v1;\nvolatile u32 *q;\nv1 = *(volatile u32 *)0x70001018;\nq = (volatile u32 *)(v1 + 32);\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
]

# a-form (0x70000000 in a variable)
a_forms = [
    ("u32 a; u32 v1; u32 q; a=0x70000000; v1=*(u32*)(a+4120); q=v1+32",
     "u32 a;\nu32 v1;\nu32 q;\na = 0x70000000;\nv1 = *(volatile u32 *)(a + 4120);\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
    ("u32 a; u32 v1; volatile u32 q; ...",
     "u32 a;\nu32 v1;\nvolatile u32 q;\na = 0x70000000;\nv1 = *(volatile u32 *)(a + 4120);\nq = v1 + 32;\n*(volatile s8 *)q = *(volatile s8 *)q & -2;"),
]

allforms = forms + chain_forms + scaled_forms + a_forms
for i, (name, body) in enumerate(allforms):
    src = TYPEDEFS + f"void func_001F4710(void)\n{{\n    {body}\n}}\n"
    add(name, src)

# Build spec
parts = []
for i, (name, src) in enumerate(cands):
    parts.append(f"VA 001F4710\nSIZE 1E\nCOMP 3.0.1b210\nEND\n{src}---\n")
open(f"{ROOT}/pilots/spec_sweep.txt", "w").write("".join(parts))
print(f"wrote {len(cands)} candidates to {ROOT}/pilots/spec_sweep.txt")

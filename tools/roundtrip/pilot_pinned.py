#!/usr/bin/env python3
"""Hand-validation of the pinned-register-file pattern on func_00223500.

Takes the generated C (/tmp/one_2_2_auto.c), rewrites the two stacked-gap
sites into pinned form (asm-var register file + empty-volatile tie
statements + "0"-matching addu), injects the SP_LW0_R2/R3 defines, and
builds a spec for install_wins2.
"""
import re
import subprocess
import sys

SRC = "/tmp/one_2_2_auto.c"
OUT = "/tmp/spec_pinned.txt"
G = "/home/user/sfzfg/roundtrip"

src = open(SRC).read()

# 1) inject per-site-value chain-direct lw defines after SP_LW define
anchor = '#define SP_LW(off) '
i = src.find(anchor)
line_end = src.find("\n", i)
inject = (
    '#define SP_LW0_R2(k) ({ register u32 r asm("$2"); '
    '__asm__ volatile("lui $2,0x7000\\n\\tlw $2," #k "($2)" : "=r"(r)); r; })\n'
    '#define SP_LW0_R3(k) ({ register u32 r asm("$3"); '
    '__asm__ volatile("lui $2,0x7000\\n\\tlw $3," #k "($2)" : "=r"(r)); r; })\n'
)
src = src[:line_end + 1] + inject + src[line_end + 1:]

# 2) pinned register-file decls after the function's opening decl block
decl = ('    register u32 SP_r2 asm("$2");\n'
        '    register u32 SP_r3 asm("$3");\n')
body_at = src.find("void func_00223500(void)\n{\n")
assert body_at >= 0
insert_at = body_at + len("void func_00223500(void)\n{\n") + 1  # after first \n of decls
src = src[:insert_at] + decl + src[insert_at:]

# 3) site A: double lh + addu (insn order: lh->$3, lh->$2, addu $3,$3,$2)
siteA_old = ("    SP_SH_D(0x112C, SP_ADDU2_T3(SP_LH0_R3(0x112C), "
             "SP_LH0_R2(0x112C)));")
siteA_new = (
    '    __asm__ volatile("" : "=r"(SP_r3) : "0"(SP_LH0_R3(0x112C)));\n'
    '    __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_LH0_R2(0x112C)));\n'
    '    __asm__ volatile("addu %0,%1,%2" : "=r"(SP_r3) : "0"(SP_r3), '
    '"r"(SP_r2));\n'
    "    SP_SH_D(0x112C, SP_r3);")
assert siteA_old in src, "site A text not found"
src = src.replace(siteA_old, siteA_new)

# 4) site B: lw->$3, lh->$2 (+pair in-place), addu $3,$3,$2, store
siteB_old = ("    SP_W16TO(SP_w1, SP_LH0_R2(0x112C));\n"
             "    SP_SW_D(0x1108, SP_ADDU2_T3(SP_LW(0x1108), SP_w1));")
siteB_new = (
    '    __asm__ volatile("" : "=r"(SP_r3) : "0"(SP_LW0_R3(0x1108)));\n'
    '    __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_LH0_R2(0x112C)));\n'
    '    __asm__ volatile("dsll32 %0,%0,0x10\\n\\tdsra32 %0,%0,0x10" '
    ': "+r"(SP_r2));\n'
    '    __asm__ volatile("addu %0,%1,%2" : "=r"(SP_r3) : "0"(SP_r3), '
    '"r"(SP_r2));\n'
    "    SP_SW_D(0x1108, SP_r3);")
assert siteB_old in src, "site B text not found"
src = src.replace(siteB_old, siteB_new)

open("/tmp/pinned_00223500.c", "w").write(src)
va, size = 0x00223500, 0x170
open(OUT, "w").write(
    f"VA {va:08X}\nSIZE {size:X}\nCOMP ee-gcc2.96\nEND\n{src}---\n")
print("patched spec written; verifying...")
r = subprocess.run(["python3", f"{G}/pilots/install_wins2.py", OUT],
                   capture_output=True, text=True)
print(r.stdout.strip()[-400:] or r.stderr.strip()[-400:])

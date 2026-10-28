#!/usr/bin/env python3
"""Full asm-macro reconstruction of func_0025A3A0 on ee-gcc 2.96.

Model: the original source used SDK-style access macros whose asm blocks
chain through $3 (v1).  Each access = one asm volatile block, so gcc never
CSEs or moves them; the C carries only structure (conditions, arithmetic).
"""
import re
import subprocess

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

G = "/home/user/sfzfg/compilers/ee-gcc2.96/bin/ee-gcc"
AS = "/home/user/sfzfg/compilers/ee-gcc2.96/ee/bin/as"
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
img = open("ro9_original.bin", "rb").read()
TGT = [f"{i.mnemonic} {i.op_str}"
       for i in md.disasm(img[0x25A3A0 - 0x1F0000:0x25A3A0 - 0x1F0000 + 80], 0x25A3A0)]

SRC = r'''typedef unsigned int u32;
#define SP_SW0(off) __asm__ volatile("lui $3,0x7000\n\tsw $0," #off "($3)")
#define SP_LW(off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #off "($3)" : "=r"(r)); r; })
#define SP_LB(ch, k) ({ register signed char r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlb $3," #k "($3)" : "=r"(r)); r; })
#define SP_SB0(ch, k) __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tsb $0," #k "($3)")
#define SP_SWV(off, val) __asm__ volatile("lui $3,0x7000\n\tsw %0," #off "($3)" :: "r"(val))
void f(void) {
    long long v;
    SP_SW0(0x1158);
    v = SP_LB(0x1118, 0x34);
    SP_SWV(0x1150, v);
    if (SP_LW(0x1150)) {
        SP_SB0(0x1118, 0xb);
    }
}
'''
# simpler store form too
SRC2 = SRC

open("/tmp/g2.c", "w").write(SRC)
for fl in ("-O1", "-O2"):
    r = subprocess.run([G, fl, "-S", "-o", "/tmp/g2.s", "/tmp/g2.c"],
                       capture_output=True, text=True)
    if r.returncode:
        print(fl, "COMPILE FAIL:", r.stderr[-300:])
        continue
    txt = re.sub(r"\blbu\b", "lb", re.sub(r"\blhu\b", "lh", open("/tmp/g2.s").read()))
    open("/tmp/g2.s", "w").write(txt)
    subprocess.run([AS, "-EL", "-o", "/tmp/g2.o", "/tmp/g2.s"], capture_output=True)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary",
                    "--only-section=.text", "/tmp/g2.o", "/tmp/g2.bin"],
                   capture_output=True)
    got = [f"{i.mnemonic} {i.op_str}"
           for i in md.disasm(open("/tmp/g2.bin", "rb").read(), 0x25A3A0)]
    exact = sum(1 for k in range(min(len(got), len(TGT))) if got[k] == TGT[k])
    print(f"--- asm-macro chained, {fl}: {len(got)*4}B exact={exact}/{len(TGT)}")
    for k in range(max(len(got), len(TGT))):
        g = got[k] if k < len(got) else "-"
        t = TGT[k] if k < len(TGT) else "-"
        print((" " if g == t else "*") + f" {g:30s} | {t}")
    if got[:len(TGT)] == TGT:
        print("EXACT MATCH!!!")

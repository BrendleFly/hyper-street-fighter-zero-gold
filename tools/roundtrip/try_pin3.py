#!/usr/bin/env python3
"""func_0025A3A0 reconstruction v3: widen-in-macro store."""
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
#define SP_SW_W8(off, cval) __asm__ volatile("dsll32 $4,%0,0x18\n\tdsra32 $4,$4,0x18\n\tlui $3,0x7000\n\tsw $4," #off "($3)" :: "r"(cval))
void f(void) {
    SP_SW0(0x1158);
    SP_SW_W8(0x1150, SP_LB(0x1118, 0x34));
    if (SP_LW(0x1150)) {
        SP_SB0(0x1118, 0xb);
    }
}
'''
open("/tmp/g3.c", "w").write(SRC)
for fl in ("-O1", "-O2"):
    r = subprocess.run([G, fl, "-S", "-o", "/tmp/g3.s", "/tmp/g3.c"],
                       capture_output=True, text=True)
    if r.returncode:
        print(fl, "COMPILE FAIL:", r.stderr[-300:])
        continue
    subprocess.run([AS, "-EL", "-o", "/tmp/g3.o", "/tmp/g3.s"], capture_output=True)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary",
                    "--only-section=.text", "/tmp/g3.o", "/tmp/g3.bin"],
                   capture_output=True)
    got = [f"{i.mnemonic} {i.op_str}"
           for i in md.disasm(open("/tmp/g3.bin", "rb").read(), 0x25A3A0)]
    exact = sum(1 for k in range(min(len(got), len(TGT))) if got[k] == TGT[k])
    print(f"--- v3, {fl}: {len(got)*4}B exact={exact}/{len(TGT)}")
    for k in range(max(len(got), len(TGT))):
        g = got[k] if k < len(got) else "-"
        t = TGT[k] if k < len(TGT) else "-"
        print((" " if g == t else "*") + f" {g:30s} | {t}")
    if got[:len(TGT)] == TGT:
        print("EXACT MATCH!!!")

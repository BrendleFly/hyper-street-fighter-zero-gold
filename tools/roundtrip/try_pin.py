#!/usr/bin/env python3
"""Pin-register asm-macro experiment for func_0025A3A0 on ee-gcc 2.96."""
import re
import subprocess

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

G = "/home/user/sfzfg/compilers/ee-gcc2.96/bin/ee-gcc"
AS = "/home/user/sfzfg/compilers/ee-gcc2.96/ee/bin/as"
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
img = open("ro9_original.bin", "rb").read()
TGT = [f"{i.mnemonic} {i.op_str}"
       for i in md.disasm(img[0x25A3A0 - 0x1F0000:0x25A3A0 - 0x1F0000 + 80], 0x25A3A0)]

SRC = '''typedef unsigned int u32;
#define SBASE ({ register u32 r asm("$3"); __asm__ volatile("lui %0,0x7000" : "=r"(r)); r; })
void f(void) {
    register long long v asm("$4");
    *(volatile u32 *)(SBASE + 0x1158) = 0;
    v = *(volatile signed char *)(*(volatile u32 *)(SBASE + 0x1118) + 0x34);
    *(volatile u32 *)(SBASE + 0x1150) = v;
    if (*(volatile u32 *)(SBASE + 0x1150)) {
        *(volatile signed char *)(*(volatile u32 *)(SBASE + 0x1118) + 0xb) = 0;
    }
}
'''
open("/tmp/g1.c", "w").write(SRC)
for fl in ("-O1", "-O2"):
    r = subprocess.run([G, fl, "-S", "-o", "/tmp/g1.s", "/tmp/g1.c"],
                       capture_output=True, text=True)
    if r.returncode:
        print(fl, "COMPILE FAIL", r.stderr[-200:])
        continue
    txt = re.sub(r"\blbu\b", "lb", re.sub(r"\blhu\b", "lh", open("/tmp/g1.s").read()))
    open("/tmp/g1.s", "w").write(txt)
    subprocess.run([AS, "-EL", "-o", "/tmp/g1.o", "/tmp/g1.s"], capture_output=True)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary",
                    "--only-section=.text", "/tmp/g1.o", "/tmp/g1.bin"],
                   capture_output=True)
    got = [f"{i.mnemonic} {i.op_str}"
           for i in md.disasm(open("/tmp/g1.bin", "rb").read(), 0x25A3A0)]
    exact = sum(1 for k in range(min(len(got), len(TGT))) if got[k] == TGT[k])
    print(f"--- pinned regs, {fl}: {len(got)*4}B exact={exact}/{len(TGT)}")
    for k in range(max(len(got), len(TGT))):
        g = got[k] if k < len(got) else "-"
        t = TGT[k] if k < len(TGT) else "-"
        print((" " if g == t else "*") + f" {g:30s} | {t}")
    if got[:len(TGT)] == TGT:
        print("EXACT MATCH!!!")

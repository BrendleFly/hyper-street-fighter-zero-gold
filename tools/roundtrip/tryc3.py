#!/usr/bin/env python3
"""Test whether mwccps2 3.0b38 emits a direct jal for extern calls under
different declaration styles; and whether 2.4.1.01 can match the sd frame."""
import subprocess, os, sys
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

MW3 = "/home/user/sfzfg/compilers/mwcps2-3.0b38/mwccps2.exe"
MW2 = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

TARGET_VA = 0x004B5E70
TARGET_SZ = 48
tgt = img[TARGET_VA - 0x1F0000: TARGET_VA - 0x1F0000 + TARGET_SZ]

DECLS = {
    "proto-void": "extern void callee(void);",
    "k&r": "extern void callee();",
    "proto-int": "extern int callee(int);",
    "noextern": "void callee();",
}
BODY = """typedef unsigned int u32;
{decl}
void func_004B5E70(void)
{{
    u32 a;

    callee();
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = 0;
    callee();
}}
"""

for mw, label in [(MW3, "3.0b38"), (MW2, "2.4.1.01")]:
    for dtag, decl in DECLS.items():
        src = BODY.format(decl=decl)
        open("/tmp/f.c", "w").write(src)
        o = "/tmp/f.o"
        if os.path.exists(o):
            os.remove(o)
        r = subprocess.run([WIBO, mw, "-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly",
                            "-sdatathreshold", "0", "-o", o, "/tmp/f.c"], capture_output=True, text=True)
        if not os.path.exists(o):
            print(f"{label} {dtag}: compile fail")
            continue
        subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/f.bin"],
                       check=False)
        got = open("/tmp/f.bin", "rb").read()
        gl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(got, TARGET_VA)]
        tl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(tgt, TARGET_VA)]
        print(f"--- {label} {dtag}: got {len(got)}B")
        for i in range(max(len(gl), len(tl))):
            g = gl[i] if i < len(gl) else "-"
            t = tl[i] if i < len(tl) else "-"
            print(f"   {' ' if g == t else '*'} {g:<30} | {t}")
        # also check relocations (does the .o have a R_MIPS_26 against callee?)
        rel = subprocess.run(["mipsel-linux-gnu-objdump", "-r", o], capture_output=True, text=True).stdout
        has_rel = "callee" in rel
        print(f"    relocation-to-callee: {has_rel}")

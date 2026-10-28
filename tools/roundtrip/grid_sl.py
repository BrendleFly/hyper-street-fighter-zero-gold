#!/usr/bin/env python3
"""Grid-search ee-gcc shapes x flags for func_0025A3A0, +sl rewrite, and
report the FIRST MISMATCH line + remat count (how many `lui $vX, 0x7000`)
so the target's rematerialising personality can be identified."""
import re
import subprocess
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
G = "/home/user/sfzfg/compilers/ee-gcc2.96/bin/ee-gcc"
AS = "/home/user/sfzfg/compilers/ee-gcc2.96/ee/bin/as"
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
TGT = [f"{i.mnemonic} {i.op_str}"
       for i in md.disasm(img[0x25A3A0 - 0x1F0000:0x25A3A0 - 0x1F0000 + 80], 0x25A3A0)]

HDR = "typedef unsigned char u8; typedef unsigned short u16; typedef unsigned int u32;\n"
SHAPES = {
    "reuse": """
void f(void) {
    unsigned int a; long long v;
    a = 0x70000000; *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000; a = *(volatile u32 *)(a + 0x1118);
    v = *(volatile signed char *)(a + 0x34);
    a = 0x70000000; *(volatile u32 *)(a + 0x1150) = v;
    a = 0x70000000;
    if (*(volatile u32 *)(a + 0x1150)) {
        a = 0x70000000; a = *(volatile u32 *)(a + 0x1118);
        *(volatile signed char *)(a + 0xb) = 0;
    }
}
""",
    "vptr": """
void f(void) {
    unsigned int a; volatile signed char *p; long long v;
    a = 0x70000000; *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000; p = (volatile signed char *)*(volatile u32 *)(a + 0x1118);
    v = p[0x34];
    a = 0x70000000; *(volatile u32 *)(a + 0x1150) = v;
    a = 0x70000000;
    if (*(volatile u32 *)(a + 0x1150)) {
        a = 0x70000000; p = (volatile signed char *)*(volatile u32 *)(a + 0x1118);
        p[0xb] = 0;
    }
}
""",
    "nested": """
void f(void) {
    unsigned int a; s8typedefplaceholder
    a = 0x70000000; *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000; a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 0x1150) = *(volatile signed char *)(a + 0x34);
    a = 0x70000000;
    if (*(volatile u32 *)(a + 0x1150)) {
        a = 0x70000000; a = *(volatile u32 *)(a + 0x1118);
        *(volatile signed char *)(a + 0xb) = 0;
    }
}
""",
}
SHAPES["nested"] = SHAPES["nested"].replace("s8typedefplaceholder\n", "long long v;\n    v = 0;")
FLAGS = ["-O1", "-O2", "-O2 -fno-expensive-optimizations",
         "-O1 -fno-expensive-optimizations", "-O2 -fno-cse-follow-jumps -fno-cse-skip-blocks"]

for sname, body in SHAPES.items():
    for fl in FLAGS:
        src = HDR + body
        open("/tmp/g1.c", "w").write(src)
        r = subprocess.run([G] + fl.split() + ["-S", "-o", "/tmp/g1.s", "/tmp/g1.c"],
                           capture_output=True, text=True)
        if not r.returncode == 0:
            print(f"{sname:8s} {fl:42s} COMPILE FAIL")
            continue
        txt = re.sub(r"\blbu\b", "lb", re.sub(r"\blhu\b", "lh", open("/tmp/g1.s").read()))
        open("/tmp/g1.s", "w").write(txt)
        subprocess.run([AS, "-EL", "-o", "/tmp/g1.o", "/tmp/g1.s"], capture_output=True)
        subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary",
                        "--only-section=.text", "/tmp/g1.o", "/tmp/g1.bin"], capture_output=True)
        got = [f"{i.mnemonic} {i.op_str}"
               for i in md.disasm(open("/tmp/g1.bin", "rb").read(), 0x25A3A0)]
        remat = sum(1 for l in got if "lui" in l and "0x7000" in l)
        tremat = sum(1 for l in TGT if "lui" in l and "0x7000" in l)
        first = next((k for k in range(min(len(got), len(TGT))) if got[k] != TGT[k]), -1)
        exact = sum(1 for k in range(min(len(got), len(TGT))) if got[k] == TGT[k])
        print(f"{sname:8s} {fl:42s} {len(got):3d}B remat={remat}(tgt {tremat}) "
              f"exactlines={exact}/{len(TGT)} firstbad={first}")
        if exact >= len(TGT) - 4:
            for k in range(max(len(got), len(TGT))):
                g = got[k] if k < len(got) else "-"
                t = TGT[k] if k < len(TGT) else "-"
                m = " " if g == t else "*"
                print(f"  {m} {g:34s} | {t}")

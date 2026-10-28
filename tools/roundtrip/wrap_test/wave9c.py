import subprocess, os, glob, re, hashlib
from collections import defaultdict

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
ROOT = "/home/user/sfzfg/roundtrip"
SRC = f"{ROOT}/src_ro9"
BUILD = f"{ROOT}/build_eabi"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()

funcs = []
for p in glob.glob(f"{ROOT}/ro9/func_*.s"):
    va = int(re.search(r"func_([0-9A-Fa-f]{8})", os.path.basename(p)).group(1), 16)
    n = sum(1 for l in open(p) if re.match(r"\s+\.word", l))
    funcs.append((va, n * 4))
groups = defaultdict(list)
for va, sz in funcs:
    groups[hashlib.md5(img[va - 0x1F0000: va - 0x1F0000 + sz]).hexdigest()].append((va, sz))

def group_of(va0):
    sz0 = next(s for v, s in funcs if v == va0)
    return groups[hashlib.md5(img[va0 - 0x1F0000: va0 - 0x1F0000 + sz0]).hexdigest()]

T_420 = """typedef signed char s8;
typedef unsigned int u32;

void func_{name}(void)
{{
    u32 a;
    s8 v;

    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    *(volatile u32 *)(a + 0x1150) = v & 4;
}}
"""

T_A91 = """typedef signed char s8;
typedef signed short s16;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

void func_{name}(void)
{{
    u32 a;
    s8 b;
    s16 w;

    a = 0x70000000;
    b = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x379);
    *(volatile u8 *)(a + 0x1124) = b;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    w = *(volatile s16 *)(a + 0x1124);
    w &= 0x77;
    *(volatile u16 *)(a + 0x1124) = w;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = w;
}}
"""

T_1DA = """typedef unsigned char u8;
typedef unsigned int u32;

void func_{name}(void)
{{
    u32 a;
    volatile u32 *q;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x44);
    a = 0x70000000;
    q = (volatile u32 *)(*(volatile u32 *)(a + 0x1118));
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) += *(volatile u32 *)((volatile u8 *)q + 0x14);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) += *(volatile u32 *)((volatile u8 *)q + 0x4c);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x44) = *(volatile u32 *)(a + 0x1124);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = *(volatile u32 *)(a + 0x1124);
}}
"""

new_entries = []
for tag, va0, tpl in [("chk-x3-420DE0", 0x00420DE0, T_420),
                      ("chk-x3-A910", 0x0036A910, T_A91),
                      ("chk-x10-1DA0", 0x00301DA0, T_1DA)]:
    src = tpl.format(name=f"{va0:08X}")
    open(f"{SRC}/func_{va0:08X}.c", "w").write(src)
    o = f"/tmp/w9c.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"{SRC}/func_{va0:08X}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{tag}: COMPILE FAIL"); continue
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin", "rb").read()
    sz0 = next(s for v, s in funcs if v == va0)
    tgt = img[va0 - 0x1F0000: va0 - 0x1F0000 + sz0]
    if got == tgt:
        print(f"{tag}: FULL MATCH"); pad = 0
    elif len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
        pad = len(tgt) - len(got)
        print(f"{tag}: MATCH + {pad}B pad")
    else:
        print(f"{tag}: mismatch (got {len(got)}B vs {sz0}B)")
        for i in range(0, min(len(got), len(tgt)), 4):
            g, t = got[i:i+4].hex(), tgt[i:i+4].hex()
            if g != t:
                print(f"    word {i//4}: got {g} want {t}")
        continue
    for va, sz in group_of(va0):
        stem = f"func_{va:08X}"
        open(f"{SRC}/{stem}.c", "w").write(tpl.format(name=f"{va:08X}"))
        oo = f"{BUILD}/{stem}.o"
        subprocess.run([WIBO, MW] + CFLAGS + ["-o", oo, f"{SRC}/{stem}.c"], capture_output=True, text=True)
        subprocess.run(["mipsel-linux-gnu-objcopy", "--set-section-alignment", ".text=4", oo, oo + ".t"], check=True)
        os.replace(oo + ".t", oo)
        if pad:
            subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", oo, "/tmp/t.bin"], check=False)
            body = open("/tmp/t.bin", "rb").read() + bytes(pad)
            open("/tmp/padded.bin", "wb").write(body)
            subprocess.run(["mipsel-linux-gnu-objcopy", "--update-section", ".text=/tmp/padded.bin", oo, oo + ".p"], check=True)
            os.replace(oo + ".p", oo)
        new_entries.append((stem, pad))
    print(f"  -> {len(group_of(va0))} members installed")

mf = f"{SRC}/matched.txt"
lines = [l.strip() for l in open(mf) if l.strip()]
existing = {l.split(":")[0] for l in lines}
for stem, pad in new_entries:
    if stem.split(":")[0] not in existing:
        lines.append(f"{stem}:{pad}" if pad else stem)
lines = sorted(set(lines), key=lambda x: x.split(":")[0])
open(mf, "w").write("\n".join(lines) + "\n")
print(f"matched.txt: {len(lines)} entries")

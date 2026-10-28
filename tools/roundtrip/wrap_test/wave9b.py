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

def compile_body(c_text, va):
    open(f"{SRC}/func_{va:08X}.c", "w").write(c_text)
    o = f"/tmp/w9b_{va:08X}.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"{SRC}/func_{va:08X}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        return None
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    return open("/tmp/g.bin", "rb").read()

def apply_group(members, c_tpl, expect_len, tag):
    va0 = members[0][0]
    got = compile_body(c_tpl.format(name=f"{va0:08X}"), va0)
    if got is None:
        print(f"{tag}: compile fail"); return []
    tgt = img[va0 - 0x1F0000: va0 - 0x1F0000 + members[0][1]]
    if tgt[:len(got)] != got or set(tgt[len(got):]) - {0}:
        print(f"{tag}: body mismatch (got {len(got)}B)")
        for i in range(0, min(len(got), len(tgt)), 4):
            g, t = got[i:i+4].hex(), tgt[i:i+4].hex()
            if g != t:
                print(f"    word {i//4}: got {g} want {t}")
        return []
    pad = members[0][1] - len(got)
    out = []
    for va, sz in members:
        stem = f"func_{va:08X}"
        open(f"{SRC}/{stem}.c", "w").write(c_tpl.format(name=f"{va:08X}"))
        o = f"{BUILD}/{stem}.o"
        subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"{SRC}/{stem}.c"], capture_output=True, text=True)
        subprocess.run(["mipsel-linux-gnu-objcopy", "--set-section-alignment", ".text=4", o, o + ".t"], check=True)
        os.replace(o + ".t", o)
        if pad:
            subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/t.bin"], check=False)
            body = open("/tmp/t.bin", "rb").read() + bytes(pad)
            open("/tmp/padded.bin", "wb").write(body)
            subprocess.run(["mipsel-linux-gnu-objcopy", "--update-section", ".text=/tmp/padded.bin", o, o + ".p"], check=True)
            os.replace(o + ".p", o)
        out.append((stem, pad))
    print(f"{tag}: applied to {len(out)} members (pad={pad})")
    return out

# group A: 64x do-nothing (jr ra; nop x3)
VOID_TPL = """void func_{name}(void)
{{
}}
"""
members = group_of(0x002294C0)
new_a = apply_group(members, VOID_TPL, 16, "void-x64") if len(members) > 50 else []
if new_a:
    print("  check body was:", img[0x002294C0-0x1F0000:0x002294C0-0x1F0000+16].hex(" "))

# group B: 3x 32B scratchpad clear variant @0x283D00
B_TPL = """typedef unsigned char u8;
typedef unsigned int u32;

void func_{name}(void)
{{
    u32 a;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = 0;
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1114) + 0x181) = 0;
}}
"""
new_b = apply_group(group_of(0x00283D00), B_TPL, 32, "clear-x3")

# update matched.txt
mf = f"{SRC}/matched.txt"
lines = [l.strip() for l in open(mf) if l.strip()]
existing = {l.split(":")[0] for l in lines}
for stem, pad in new_a + new_b:
    if stem not in existing:
        lines.append(f"{stem}:{pad}" if pad else stem)
lines = sorted(set(lines), key=lambda x: x.split(":")[0])
open(mf, "w").write("\n".join(lines) + "\n")
print(f"matched.txt: {len(lines)} entries")

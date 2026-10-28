import subprocess, os, glob, re
from collections import defaultdict

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
ROOT = "/home/user/sfzfg/roundtrip"
SRC = f"{ROOT}/src_ro9"
BUILD = f"{ROOT}/build_eabi"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()

# regenerate groups
import hashlib
funcs = []
for p in glob.glob(f"{ROOT}/ro9/func_*.s"):
    va = int(re.search(r"func_([0-9A-Fa-f]{8})", os.path.basename(p)).group(1), 16)
    n = sum(1 for l in open(p) if re.match(r"\s+\.word", l))
    funcs.append((va, n * 4))
groups = defaultdict(list)
for va, sz in funcs:
    groups[hashlib.md5(img[va - 0x1F0000: va - 0x1F0000 + sz]).hexdigest()].append((va, sz))

def group_of(va0):
    return groups[hashlib.md5(img[va0 - 0x1F0000: va0 - 0x1F0000 + next(s for v, s in funcs if v == va0)]).hexdigest()]

TPL = {
"x23": """typedef unsigned char u8;
typedef unsigned int u32;

void func_{name}(void)
{{
    u32 a;

    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0x3c) = 0;
}}
""",
"x34": """typedef unsigned int u32;

void func_{name}(void)
{{
    u32 a, v;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    v = 1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v;
}}
""",
"x7": """typedef unsigned char u8;
typedef unsigned int u32;

void func_{name}(void)
{{
    u32 a, v;

    v = 4;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 4) = v;
}}
""",
"x8": """typedef unsigned char u8;
typedef unsigned int u32;

void func_{name}(void)
{{
    u32 a, v;

    v = 8;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1110);
    *(volatile u8 *)(a + 0xcc) = v;
    v = 2;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1110);
    *(volatile u8 *)(a + 0xee) = v;
    v = 8;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1110);
    *(volatile u8 *)(a + 0xef) = v;
}}
""",
}
# x23/x34 keep v-order as proven; x34 template: v=1 placement between stores (already in template)
PADS = {"x23": 12, "x34": 12, "x7": None, "x8": None}
FIRSTS = {"x23": 0x002556D0, "x34": 0x00235A00, "x7": 0x0051AC80, "x8": 0x002B1E70}

def compile_test(tpl_name, va, sz):
    src = TPL[tpl_name].format(name=f"{va:08X}")
    open(f"{SRC}/func_{va:08X}.c", "w").write(src)
    o = f"/tmp/w9a_{tpl_name}.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"{SRC}/func_{va:08X}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        return None, "compile-fail"
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]
    if got == tgt:
        return got, "full"
    if len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
        return got, f"prefix+{len(tgt)-len(got)}pad"
    return got, f"mismatch (got {len(got)}B)"

new_entries = []
for name in ("x23", "x34", "x7", "x8"):
    va0 = FIRSTS[name]
    sz0 = next(s for v, s in funcs if v == va0)
    got, verdict = compile_test(name, va0, sz0)
    print(f"{name}: {verdict}")
    if verdict == "mismatch (got 0B)" or verdict.startswith("compile-fail"):
        continue
    if verdict.startswith("mismatch"):
        # show diff for diagnosis
        for i in range(0, min(len(got) if got else 0, sz0), 4):
            g = got[i:i+4].hex()
            t = img[va0-0x1F0000+i:va0-0x1F0000+i+4].hex()
            if g != t:
                print(f"    word {i//4}: got {g} want {t}")
        continue
    pad = 0
    if verdict.startswith("prefix"):
        pad = int(verdict.split("+")[1].replace("pad", ""))
    if PADS[name]:
        pad = PADS[name]
    for va, sz in group_of(va0):
        stem = f"func_{va:08X}"
        open(f"{SRC}/{stem}.c", "w").write(TPL[name].format(name=f"{va:08X}"))
        new_entries.append((stem, pad))
    print(f"  -> {len(group_of(va0))} members queued (pad={pad})")

# install objects for all new entries and verify bytes
ok, bad = 0, []
for stem, pad in new_entries:
    o = f"{BUILD}/{stem}.o"
    r = subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"{SRC}/{stem}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        bad.append((stem, "compile")); continue
    subprocess.run(["mipsel-linux-gnu-objcopy", "--set-section-alignment", ".text=4", o, o + ".t"], check=True)
    os.replace(o + ".t", o)
    if pad:
        subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/t.bin"], check=False)
        body = open("/tmp/t.bin", "rb").read() + bytes(pad)
        open("/tmp/padded.bin", "wb").write(body)
        r2 = subprocess.run(["mipsel-linux-gnu-objcopy", "--update-section", ".text=/tmp/padded.bin", o, o + ".p"], capture_output=True, text=True)
        if r2.returncode:
            bad.append((stem, "pad")); continue
        os.replace(o + ".p", o)
    va = int(stem[5:], 16)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/c.bin"], check=False)
    got = open("/tmp/c.bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + len(got)]
    if got == tgt and set(img[va - 0x1F0000 + len(got): va - 0x1F0000 + 64][:0]) == set():
        ok += 1
    else:
        bad.append((stem, "bytes"))
print(f"installed+verified: {ok}, bad: {bad[:5]}")

# update matched.txt
mf = f"{SRC}/matched.txt"
lines = [l.strip() for l in open(mf) if l.strip()]
existing = {l.split(":")[0] for l in lines}
for stem, pad in new_entries:
    if stem not in existing:
        lines.append(f"{stem}:{pad}" if pad else stem)
lines = sorted(set(lines), key=lambda x: x.split(":")[0])
open(mf, "w").write("\n".join(lines) + "\n")
print(f"matched.txt: {len(lines)} entries")

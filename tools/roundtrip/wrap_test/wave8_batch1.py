import subprocess, os, glob, hashlib, re
from collections import defaultdict

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
ROOT = "/home/user/sfzfg/roundtrip"
SRC = f"{ROOT}/src_ro9"
BUILD = f"{ROOT}/build_eabi"

img = open(f"{ROOT}/ro9_original.bin", "rb").read()

# ---------- regenerate duplicate groups ----------
funcs = []
for p in glob.glob(f"{ROOT}/ro9/func_*.s"):
    va = int(re.search(r"func_([0-9A-Fa-f]{8})", os.path.basename(p)).group(1), 16)
    n = sum(1 for l in open(p) if re.match(r"\s+\.word", l))
    funcs.append((va, n * 4))
groups = defaultdict(list)
for va, sz in funcs:
    body = img[va - 0x1F0000: va - 0x1F0000 + sz]
    groups[hashlib.md5(body).hexdigest()].append((va, sz))

def body_of(va, sz):
    return img[va - 0x1F0000: va - 0x1F0000 + sz]

RECIPE1_MD5 = hashlib.md5(body_of(0x004C5230, 32)).hexdigest()

# ---------- formulation templates ----------
TEMPLATE_1 = """typedef unsigned int u32;

void func_{name}(void)
{{
    u32 a;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = 0;
}}
"""

TEMPLATE_36 = """typedef unsigned int u32;
typedef signed char s8;

void func_{name}(void)
{{
    u32 a;
    volatile s8 *p;

    a = 0x70000000;
    p = (volatile s8 *)(*(volatile u32 *)(a + 0x1118));
    p[4] += 2;
}}
"""

def try_match(template, group_members, tag):
    va0, sz0 = group_members[0]
    src = template.format(name=f"{va0:08X}")
    open(f"{SRC}/func_{va0:08X}.c", "w").write(src)
    o = f"/tmp/w8_{tag}.o"
    if os.path.exists(o):
        os.remove(o)
    r = subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"{SRC}/func_{va0:08X}.c"],
                       capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{tag}: COMPILE FAIL {r.stderr[:200]}")
        return False
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text",
                    o, "/tmp/w8.bin"], check=False)
    got = open("/tmp/w8.bin", "rb").read()
    tgt = body_of(va0, sz0)
    if got == tgt:
        print(f"{tag}: MATCH ({len(group_members)} members)")
        return True
    print(f"{tag}: no match (got {len(got)}B vs {sz0}B)")
    for i in range(0, min(len(got), len(tgt)), 4):
        g, t = got[i:i+4].hex(), tgt[i:i+4].hex()
        if g != t:
            print(f"   word {i//4}: got {g} want {t}")
    return False

matched_new = []

# ---------- A) recipe-1 group expansion (x46) ----------
members = groups[RECIPE1_MD5]
print(f"recipe-1 group: {len(members)} members")
already = {"004C5230","004CC180","002A8C80","00399AB0","00489850","002CA3D0","003BF0D0","002ECA10","0027B5D0"}
for va, sz in members:
    stem = f"func_{va:08X}"
    if f"{va:08X}" in already:
        continue
    open(f"{SRC}/{stem}.c", "w").write(TEMPLATE_1.format(name=f"{va:08X}"))
    matched_new.append(stem)
print(f"new recipe-1 .c files: {len(matched_new)}")

# ---------- B) x36 counter group ----------
G36 = None
for md5, mem in groups.items():
    if len(mem) >= 30 and mem[0][1] == 32 and mem[0][0] == 0x255590:
        G36 = mem
# x36: body is 28 bytes + 4 bytes trailing pad in the 32B slot
import hashlib as _h
G36_BODY = _h.md5(body_of(0x255590, 32)).hexdigest()
G36 = groups[G36_BODY]
va0, _ = G36[0]
open(f"{SRC}/func_{va0:08X}.c", "w").write(TEMPLATE_36.format(name=f"{va0:08X}"))
o = "/tmp/w8_x36b.o"
subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"{SRC}/func_{va0:08X}.c"], capture_output=True, text=True)
subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/w8b.bin"], check=False)
got = open("/tmp/w8b.bin", "rb").read()
tgt = body_of(va0, 32)
if tgt.startswith(got) and set(tgt[len(got):]) <= {0}:
    print(f"x36: BODY MATCH + {len(tgt)-len(got)}B pad ({len(G36)} members)")
    for va, sz in G36:
        stem = f"func_{va:08X}"
        open(f"{SRC}/{stem}.c", "w").write(TEMPLATE_36.format(name=f"{va:08X}"))
        matched_new.append(f"{stem}:{len(tgt)-len(got)}")
else:
    print(f"x36: still no body match (got {len(got)}B)")

# ---------- C) compile + verify EVERY new .c, install into build ----------
ok = 0
bad = []
for entry in matched_new:
    stem = entry.split(":")[0]
    o = f"{BUILD}/{stem}.o"
    r = subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"{SRC}/{stem}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        bad.append((stem, "compile"))
        continue
    subprocess.run(["mipsel-linux-gnu-objcopy", "--set-section-alignment", ".text=4", o, o + ".t"], check=True)
    os.replace(o + ".t", o)
    va = int(stem[5:], 16)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/c.bin"], check=False)
    got = open("/tmp/c.bin", "rb").read()
    if got == body_of(va, len(got)) and len(got) == 32:
        ok += 1
    else:
        bad.append((stem, "bytes"))
print(f"installed+verified: {ok}, bad: {bad[:5]}")

# ---------- D) update matched.txt ----------
mf = f"{SRC}/matched.txt"
lines = [l.strip() for l in open(mf) if l.strip()]
lines = [l.split(":")[0] for l in lines]
for stem in matched_new:
    base = stem.split(":")[0]
    lines = [l for l in lines if l.split(":")[0] != base]
    lines.append(stem)
lines = sorted(set(lines))
open(mf, "w").write("\n".join(lines) + "\n")
print(f"matched.txt now: {len(lines)} entries")

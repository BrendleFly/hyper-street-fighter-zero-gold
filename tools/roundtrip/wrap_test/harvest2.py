#!/usr/bin/env python3
"""Tier-2 harvest: linear v1-based scratchpad load/store chains -> generated C."""
import struct, hashlib, glob, re, os, subprocess
from collections import defaultdict

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
ROOT = "/home/user/sfzfg/roundtrip"
SRC = f"{ROOT}/src_ro9"
BUILD = f"{ROOT}/build_eabi"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()

REG = ['zero','at','v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7',
       's0','s1','s2','s3','s4','s5','s6','s7','t8','t9','k0','k1','gp','sp','fp','ra']

LOAD_OP = {0x23: ('u32', 'lw'), 0x20: ('s8', 'lb'), 0x24: ('u8', 'lbu'),
           0x21: ('s16', 'lh'), 0x25: ('u16', 'lhu')}
STORE_OP = {0x2b: ('u32',), 0x28: ('u8',), 0x29: ('u16',)}

def decode_ops(body):
    """Decode a linear scratchpad chain; return ops list or None."""
    ops = []
    i = 0
    n = len(body)
    while i < n:
        w = struct.unpack_from("<I", body, i)[0]
        op = w >> 26
        if w == 0x3c037000 or w == 0x03e00008 or w == 0:
            i += 4
            continue
        rs = (w >> 21) & 31
        rt = (w >> 16) & 31
        imm = w & 0xFFFF
        if imm >= 0x8000:
            imm -= 0x10000
        if op in LOAD_OP and rs == 3:
            ops.append(("load", REG[rt], LOAD_OP[op][0], imm))
            i += 4
            continue
        if op in STORE_OP and rs == 3:
            ops.append(("store", REG[rt], STORE_OP[op][0], imm))
            i += 4
            continue
        if op == 0x09 and rs == 0:
            # li rt, imm — value materialization; record, keep scanning
            ops.append(("li", REG[rt], "u32", imm))
            i += 4
            continue
        return None
    return ops or None

def gen_c(name, ops):
    # track which register holds which C variable; v1's slot is the base var 'a'
    lines = []
    types = ["typedef signed char s8;", "typedef unsigned char u8;",
             "typedef signed short s16;", "typedef unsigned short u16;",
             "typedef unsigned int u32;"]
    var_by_reg = {}
    body = []
    for kind, reg, typ, off in ops:
        base = var_by_reg.get("v1", "a")
        if base == "a" and "a" not in var_by_reg.values():
            body.append("    a = 0x70000000;")
        if kind == "load":
            if reg == "v1":
                v = base
                body.append(f"    {v} = *(volatile {typ} *)({v} + {off:#x});")
            else:
                vn = reg if reg not in var_by_reg.values() else reg + "_"
                var_by_reg[reg] = vn
                decl = f"    volatile {typ} {vn};\n" if False else None
                body.append(f"    {vn} = *(volatile {typ} *)({base} + {off:#x});")
            var_by_reg[reg] = var_by_reg.get(reg, ("v" + reg) if reg != "v1" else base)
        else:
            srcval = "0" if reg == "zero" else var_by_reg.get(reg, reg)
            body.append(f"    *(volatile {typ} *)({base} + {off:#x}) = {srcval};")
        if kind == "load" and reg == "v1":
            var_by_reg["v1"] = base
    return None  # replaced below


def gen_c2(name, ops):
    """Fully-nested form."""
    decls = ["    u32 a;"]
    used = {"a"}
    lines = []
    valvar = {}
    def val(reg):
        if reg == "zero":
            return "0"
        v = valvar.get(reg)
        if v is None:
            v = "v" if "v" not in used else "w"
            used.add(v)
            decls.append(f"    u32 {v};")
            valvar[reg] = v
        return v
    for kind, reg, typ, off in ops:
        if kind == "li":
            v = val(reg)
            lines.append(f"    {v} = {off:#x};")
        elif kind == "load":
            v = val(reg)
            lines.append("    a = 0x70000000;")
            lines.append(f"    {v} = *(volatile {typ} *)(*(volatile u32 *)(a + 0x1118) + {off:#x});")
        else:
            sv = val(reg)
            lines.append("    a = 0x70000000;")
            lines.append(f"    *(volatile {typ} *)(*(volatile u32 *)(a + 0x1118) + {off:#x}) = {sv};")
    hdr = ("typedef signed char s8;" + chr(10) + "typedef unsigned char u8;" + chr(10)
           + "typedef signed short s16;" + chr(10) + "typedef unsigned short u16;" + chr(10)
           + "typedef unsigned int u32;" + chr(10) + chr(10))
    text = (hdr + f"void func_{name}(void)" + chr(10) + "{" + chr(10)
            + chr(10).join(decls) + chr(10) + chr(10).join(lines) + chr(10) + "}" + chr(10))
    return text



def gen_c3(name, ops):
    """two-base variant: fresh base var per phase (a, b), plus int temp for values."""
    decls = ["    u32 a, b;", "    s8 v;", "    int r;"]
    lines = []
    for idx, (kind, reg, typ, off) in enumerate(ops):
        base = "a" if idx % 2 == 0 else "b"
        if kind == "li":
            lines.append(f"    v = {off};")
        elif kind == "load":
            if typ in ("u32",):
                lines.append(f"    {base} = 0x70000000;")
                lines.append(f"    v = *(volatile s8 *)(*(volatile u32 *)({base} + 0x1118) + {off:#x});")
            else:
                lines.append(f"    {base} = 0x70000000;")
                lines.append(f"    v = *(volatile {typ} *)(*(volatile u32 *)({base} + 0x1118) + {off:#x});")
        else:
            sv = "r" if reg != "zero" else "0"
            lines.append(f"    r = v & 0xFF;")
            lines.append(f"    {base} = 0x70000000;")
            lines.append(f"    *(volatile {typ} *)({base} + {off:#x}) = {sv};")
    hdr = ("typedef signed char s8;" + chr(10) + "typedef unsigned char u8;" + chr(10)
           + "typedef unsigned int u32;" + chr(10) + chr(10))
    return (hdr + f"void func_{name}(void)" + chr(10) + "{" + chr(10)
            + chr(10).join(decls) + chr(10) + chr(10).join(lines) + chr(10) + "}" + chr(10))



def gen_c_chain(name, ops):
    """w14 state machine + base-direct loads/stores.
    li -> prime fresh var. Chain load (dest v1, off<0x1100): unconditional base
    reset then a = *a+off (a becomes the pointer). Loads/stores while a is a
    pointer: direct. When a is NOT a pointer (base context): base reset + op."""
    lines = []
    decls = ["    u32 a;"]
    used = {"a"}
    varnum = [0]
    var_of_reg = {}
    a_is_ptr = False
    for kind, reg, typ, off in ops:
        if kind == "li":
            nv = fresh() if False else None
            varnum[0] += 1
            nv = f"v{varnum[0]}"
            used.add(nv)
            decls.append(f"    u32 {nv};")
            var_of_reg[reg] = nv
            lines.append(f"    {nv} = {off:#x};")
            continue
        if kind == "load":
            if reg == "v1" and off < 0x1100:
                lines.append("    a = 0x70000000;")
                lines.append(f"    a = *(volatile {typ} *)(a + {off:#x});")
                a_is_ptr = True
            else:
                nv = f"v{varnum[0] + 1}"
                varnum[0] += 1
                used.add(nv)
                decls.append(f"    volatile {typ} {nv};")
                var_of_reg[reg] = nv
                if a_is_ptr:
                    lines.append(f"    {nv} = *(volatile {typ} *)(a + {off:#x});")
                else:
                    lines.append("    a = 0x70000000;")
                    lines.append(f"    {nv} = *(volatile {typ} *)(a + {off:#x});")
            continue
        if kind == "store":
            sv = "0" if reg == "zero" else var_of_reg.get(reg, reg)
            if a_is_ptr:
                lines.append(f"    *(volatile {typ} *)(a + {off:#x}) = {sv};")
            else:
                lines.append("    a = 0x70000000;")
                lines.append(f"    *(volatile {typ} *)(a + {off:#x}) = {sv};")
            continue
    hdr = ("typedef signed char s8;" + chr(10) + "typedef unsigned char u8;" + chr(10)
           + "typedef signed short s16;" + chr(10) + "typedef unsigned short u16;" + chr(10)
           + "typedef unsigned int u32;" + chr(10) + chr(10))
    return (hdr + f"void func_{name}(void)" + chr(10) + "{" + chr(10)
            + chr(10).join(decls) + chr(10) + chr(10).join(lines) + chr(10) + "}" + chr(10))

matched = set(l.strip().split(":")[0] for l in open(f"{SRC}/matched.txt") if l.strip())
funcs = []
for p in glob.glob(f"{ROOT}/ro9/func_*.s"):
    va = int(re.search(r"func_([0-9A-Fa-f]{8})", os.path.basename(p)).group(1), 16)
    n = sum(1 for l in open(p) if re.match(r"\s+\.word", l))
    funcs.append((va, n * 4))
groups = defaultdict(list)
for va, sz in funcs:
    groups[hashlib.md5(img[va - 0x1F0000: va - 0x1F0000 + sz]).hexdigest()].append((va, sz))

results = []
seen = set()
newstems = open("/home/user/sfzfg/roundtrip/pilots/w13_new.txt", "a")
for va, sz in funcs:
    stem = f"func_{va:08X}"
    if stem in matched:
        continue
    body = img[va - 0x1F0000: va - 0x1F0000 + sz]
    ops = decode_ops(body)
    if not ops:
        continue
    key = hashlib.md5(body).hexdigest()
    if key in seen:
        continue
    seen.add(key)
    members = groups[key]
    # build candidate texts WITHOUT writing to src_ro9
    cands = []
    cc = gen_c_chain(f"{va:08X}", ops)
    if cc:
        cands.append(("chain", cc))
    cands.append(("c2", gen_c2(f"{va:08X}", ops)))
    cands.append(("c3", gen_c3(f"{va:08X}", ops)))
    win = None
    for shape_tag, ctext in cands:
        open("/tmp/cand.c", "w").write(ctext)
        for opt in (["-O1"], ["-O2"], ["-O3"], ["-O1,p"], ["-O2,p"], ["-O0"]):
            o = f"/tmp/h2_{va:08X}.o"
            if os.path.exists(o):
                os.remove(o)
            subprocess.run([WIBO, MW, "-gccinc"] + opt + ["-c", "-lang", "c", "-str", "readonly",
                           "-sdatathreshold", "0", "-o", o, "/tmp/cand.c"],
                           capture_output=True, text=True)
            if not os.path.exists(o):
                continue
            subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
            got = open("/tmp/g.bin", "rb").read()
            tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]
            pad = 0
            if got == tgt:
                pad = 0
            elif len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
                pad = len(tgt) - len(got)
            else:
                continue
            win = (shape_tag, opt, ctext, pad)
            break
        if win:
            break
    if not win:
        results.append((len(members), va, "no", 0, ()))
        continue
    shape_tag, opt, ctext, pad = win
    verdict = f"MATCH[{shape_tag}]{'+pad%d' % pad if pad else ''}"
    total = 0
    for mva, msz in members:
        stem = f"func_{mva:08X}"
        mtext = ctext.replace(f"func_{va:08X}", f"func_{mva:08X}")
        open(f"{SRC}/{stem}.c", "w").write(mtext)
        oo = f"{BUILD}/{stem}.o"
        subprocess.run([WIBO, MW, "-gccinc"] + opt + ["-c", "-lang", "c", "-str", "readonly",
                       "-sdatathreshold", "0", "-o", oo, f"{SRC}/{stem}.c"], capture_output=True, text=True)
        subprocess.run(["mipsel-linux-gnu-objcopy", "--set-section-alignment", ".text=4", oo, oo + ".t"], check=True)
        os.replace(oo + ".t", oo)
        if pad:
            subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", oo, "/tmp/t.bin"], check=False)
            b2 = open("/tmp/t.bin", "rb").read() + bytes(pad)
            open("/tmp/padded.bin", "wb").write(b2)
            subprocess.run(["mipsel-linux-gnu-objcopy", "--update-section", ".text=/tmp/padded.bin", oo, oo + ".p"], check=True)
            os.replace(oo + ".p", oo)
        total += 1
        pad_sfx = f":{pad}" if pad else ""
        newstems.write(f"{stem}{pad_sfx}" + chr(10))
    results.append((len(members), va, verdict, total, ()))
newstems.close()


wins = sum(r[3] for r in results if r[2].startswith("MATCH"))
print(f"chain-candidate groups: {len(results)}, newly matched: {wins}")
for cnt, va, verdict, total, _ in results:
    if verdict.startswith("MATCH"):
        print(f"  x{cnt} @{va:#x}: {verdict}")
fails = [(c, hex(v)) for c, v, r, t, o in results if not r.startswith("MATCH")]
print(f"failed: {len(fails)} groups, first 10: {fails[:10]}")

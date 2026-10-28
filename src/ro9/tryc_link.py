#!/usr/bin/env python3
"""Link-aware candidate tester: compiles a candidate C, swaps it into the real
build objects (auto-padded to the split slot size), relinks, and compares the
FUNCTION's bytes in the linked image.

Usage: python3 tryc_link.py <specfile>
specfile blocks: VA <hex> / SIZE <hex> / COMP <2.4|3.0> / END / <C source> / ---
"""
import subprocess, os, sys, glob, shutil
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
BUILD = f"{ROOT}/build_eabi"
LD = f"{ROOT}/ro9_fixed.ld"
IMG = f"{ROOT}/ro9_original.bin"
img = open(IMG, "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
ZERO = bytes(64)

MWS = {
    "2.4": "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe",
    "3.0": "/home/user/sfzfg/compilers/mwcps2-3.0b38/mwccps2.exe",
}
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]


def link_list():
    ents = ["header.o"]
    funs = []
    for o in glob.glob(f"{BUILD}/func_*.o"):
        stem = os.path.basename(o)[:-2]
        funs.append((int(stem[5:], 16), os.path.basename(o)))
    funs.sort()
    ents += [f for _, f in funs]
    ents.append("data.o")
    return [f"{BUILD}/{e}" for e in ents]


def link_and_extract(va, size):
    r = subprocess.run(["mipsel-linux-gnu-ld", "-T", LD, "-o", "/tmp/tl.elf"],
                       capture_output=True, text=True)
    if r.returncode:
        return None, r.stderr[:300]
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "/tmp/tl.elf", "/tmp/tl.bin"], check=False)
    data = open("/tmp/tl.bin", "rb").read()
    off = va - 0x1F0000
    return data[off:off + size], None


def pad_to_slot(o, stem):
    sfile = f"{ROOT}/ro9/{stem}.s"
    if not os.path.exists(sfile):
        return None
    slot = sum(1 for l in open(sfile) if l.strip().startswith(".word")) * 4
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text",
                    o, "/tmp/cand_text.bin"], check=False)
    csize = os.path.getsize("/tmp/cand_text.bin")
    if csize > slot:
        return None
    if csize < slot:
        body = open("/tmp/cand_text.bin", "rb").read() + ZERO[: slot - csize]
        open("/tmp/cand_pad.bin", "wb").write(body)
        subprocess.run(["mipsel-linux-gnu-objcopy", "--update-section",
                        ".text=/tmp/cand_pad.bin", o, o + ".p"], check=False)
        os.replace(o + ".p", o)
    return slot, csize


def main():
    spec = open(sys.argv[1]).read()
    n = 0
    for b in spec.split("---\n"):
        if not b.strip():
            continue
        lines = b.split("\n")
        va = size = None
        comp = "2.4"
        i = 0
        while i < len(lines):
            s = lines[i].strip()
            if s.startswith("VA "):
                va = int(s.split()[1], 16)
            elif s.startswith("SIZE "):
                size = int(s.split()[1], 16)
            elif s.startswith("COMP "):
                comp = s.split()[1]
            elif s == "END":
                i += 1
                break
            i += 1
        src = "\n".join(lines[i:])
        if va is None or size is None:
            continue
        n += 1
        stem = f"func_{va:08X}"
        open("/tmp/cand.c", "w").write(src)
        o = f"{BUILD}/{stem}.o"
        had = os.path.exists(o)
        if had:
            shutil.copy(o, "/tmp/orig_obj.o")
        # remove stale object so a failed compile cannot masquerade as a match
        if os.path.exists(o):
            os.remove(o)
        r = subprocess.run([WIBO, MWS[comp]] + CFLAGS + ["-o", o, "/tmp/cand.c"],
                           capture_output=True, text=True)
        if not os.path.exists(o):
            print(f"=== cand {n}: {stem} [{comp}] -> COMPILE FAIL {r.stderr[:150]}")
            continue
        got, err = link_and_extract(va, size)
        if got is None:
            print(f"=== cand {n}: {stem} [{comp}] -> LINK FAIL {err}")
            if had:
                shutil.copy("/tmp/orig_obj.o", o)
            continue
        tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
        if got == tgt:
            print(f"=== cand {n}: {stem} [{comp}] -> *** MATCH ***")
        else:
            diffs = sum(1 for x, y in zip(got, tgt) if x != y)
            print(f"=== cand {n}: {stem} [{comp}] -> NO ({diffs} bytes differ of {size})")
            gl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(got, va)]
            tl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(tgt, va)]
            for i in range(max(len(gl), len(tl))):
                g = gl[i] if i < len(gl) else "-"
                t = tl[i] if i < len(tl) else "-"
                if g != t:
                    print(f"    * {g:<34} | {t}")
        if had:
            shutil.copy("/tmp/orig_obj.o", o)
    print(f"done: {n} candidates")


if __name__ == "__main__":
    main()

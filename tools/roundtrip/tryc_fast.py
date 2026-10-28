#!/usr/bin/env python3
"""Fast link-aware candidate tester for SFZFG ro9.

Instead of relinking the whole 10k-object image per candidate (slow), it links
ONLY the candidate object against --defsym stubs for the callees, so call
relocations resolve to their true addresses. The candidate's .text is then
compared byte-for-byte with the original.

Usage: python3 tryc_fast.py <specfile>
"""
import subprocess, os, sys, re
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

CDIR = "/home/user/sfzfg/compilers"
MWS = {
    "2.4": f"{CDIR}/mwcps2-2.4-001213/mwccps2.exe",
    "3.0": f"{CDIR}/mwcps2-3.0b38/mwccps2.exe",
    "3.0.1b210": f"{CDIR}/mwcps2-3.0.1b210-060308/mwccps2.exe",
    "3.0.3": f"{CDIR}/mwcps2-3.0.3-020716/mwccps2.exe",
    "3.0b52": f"{CDIR}/mwcps2-3.0b52-030722/mwccps2.exe",
    "3.0.1b198": f"{CDIR}/mwcps2-3.0.1b198-051011/mwccps2.exe",
    "3.0.1b151": f"{CDIR}/mwcps2-3.0.1b151-050317/mwccps2.exe",
}
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]


def undefined_symbols(obj):
    r = subprocess.run(["mipsel-linux-gnu-nm", "-u", obj], capture_output=True, text=True)
    syms = []
    for line in r.stdout.splitlines():
        parts = line.split()
        if parts and parts[-1].startswith("func_"):
            syms.append(parts[-1])
    return syms


def sym_addr(name):
    """Address of a function symbol in ro9 (from the split file names)."""
    try:
        return int(name[5:], 16)
    except ValueError:
        return 0


def test(va, size, comp, flags, src, name):
    open("/tmp/fcand.c", "w").write(src)
    o = "/tmp/fcand.o"
    if os.path.exists(o):
        os.remove(o)
    cf = list(CFLAGS)
    if flags:
        cf = [f for f in cf if not f.startswith("-O")] + flags
    r = subprocess.run([WIBO, MWS.get(comp, MWS["2.4"])] + cf + ["-o", o, "/tmp/fcand.c"],
                       capture_output=True, text=True)
    if not os.path.exists(o):
        return f"COMPILE FAIL {r.stderr[:120]}", None
    # link candidate alone with stub symbols for its callees
    defs = []
    for s in undefined_symbols(o):
        defs += ["--defsym", f"{s}=0x{sym_addr(s):x}"]
    script = f"/tmp/fsc.ld"
    open(script, "w").write(
        f"SECTIONS {{ . = 0x{va:08X}; .text : {{ /tmp/fcand.o(.text) }} }}\n")
    lr = subprocess.run(["mipsel-linux-gnu-ld", "-T", script, "-o", "/tmp/fcand.elf"] + defs,
                        capture_output=True, text=True)
    if lr.returncode:
        return f"LINK FAIL {lr.stderr[:150]}", None
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "/tmp/fcand.elf", "/tmp/fcand.bin"],
                   check=False)
    got = open("/tmp/fcand.bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
    if got[:size] == tgt[:size]:
        return "*** MATCH ***", None
    gl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(got, va)]
    tl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(tgt, va)]
    diff = []
    for i in range(max(len(gl), len(tl))):
        g = gl[i] if i < len(gl) else "-"
        t = tl[i] if i < len(tl) else "-"
        if g != t:
            diff.append(f"    * {g:<34} | {t}")
    n = sum(1 for x, y in zip(got, tgt) if x != y)
    return f"NO ({n} bytes differ, {len(got)}B vs {size}B)", "\n".join(diff[:6])


def main():
    spec = open(sys.argv[1]).read()
    n = 0
    for b in spec.split("---\n"):
        if not b.strip():
            continue
        lines = b.split("\n")
        va = size = None
        comp = "2.4"
        flags = None
        i = 0
        while i < len(lines):
            s = lines[i].strip()
            if s.startswith("VA "):
                va = int(s.split()[1], 16)
            elif s.startswith("SIZE "):
                size = int(s.split()[1], 16)
            elif s.startswith("COMP "):
                comp = s.split()[1]
            elif s.startswith("FLAG "):
                flags = s.split()[1:]
            elif s == "END":
                i += 1
                break
            i += 1
        src = "\n".join(lines[i:])
        if va is None or size is None:
            continue
        n += 1
        try:
            verdict, detail = test(va, size, comp, flags, src, f"func_{va:08X}")
        except Exception as e:
            verdict, detail = f"ERROR {type(e).__name__}: {e}", None
        print(f"=== cand {n}: func_{va:08X} [{comp}] -> {verdict}")
        if detail:
            print(detail)
    print(f"done: {n} candidates")


if __name__ == "__main__":
    main()

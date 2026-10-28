#!/usr/bin/env python3
"""Link-aware candidate tester for SFZFG ro9.

Compiles a candidate C, swaps it into the real build objects, relinks with the
fixed-address script, and compares the FUNCTION's bytes in the linked image
(raw-object comparison cannot see relocation targets).

Usage: python3 tryc_link.py <specfile>
specfile blocks:
  VA <hex>
  SIZE <hex>            (hex bytes)
  COMP <2.4|3.0|3.0.1b210|...>
  [FLAG <compiler flags>] (optional, replaces -O1)
  END
  <C source>
  ---
"""
import subprocess, os, sys, shutil
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
BUILD = f"{ROOT}/build_eabi"
LD = f"{ROOT}/ro9_fixed.ld"
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


def link_and_extract(va, size):
    r = subprocess.run(["mipsel-linux-gnu-ld", "-T", LD, "-o", "/tmp/tl.elf"],
                       capture_output=True, text=True)
    if r.returncode:
        return None, r.stderr[:300]
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "/tmp/tl.elf", "/tmp/tl.bin"], check=False)
    data = open("/tmp/tl.bin", "rb").read()
    off = va - 0x1F0000
    return data[off:off + size], None


def run_candidate(stem, va, size, comp, flags, src):
    open("/tmp/cand.c", "w").write(src)
    o = f"{BUILD}/{stem}.o"
    had = os.path.exists(o)
    if had:
        shutil.copy(o, "/tmp/orig_obj.o")
    if os.path.exists(o):
        os.remove(o)
    cf = list(CFLAGS)
    if flags:
        cf = [f for f in cf if not f.startswith("-O")] + flags
    r = subprocess.run([WIBO, MWS.get(comp, MWS["2.4"])] + cf + ["-o", o, "/tmp/cand.c"],
                       capture_output=True, text=True)
    if not os.path.exists(o):
        if had:
            shutil.copy("/tmp/orig_obj.o", o)
        return f"COMPILE FAIL {r.stderr[:120]}", None
    got, err = link_and_extract(va, size)
    if got is None:
        if had:
            shutil.copy("/tmp/orig_obj.o", o)
        return f"LINK FAIL {err}", None
    tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
    if had:
        shutil.copy("/tmp/orig_obj.o", o)
    if got == tgt:
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
    return f"NO ({n} bytes differ)", "\n".join(diff[:6])


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
        stem = f"func_{va:08X}"
        try:
            verdict, detail = run_candidate(stem, va, size, comp, flags, src)
        except Exception as e:
            verdict, detail = f"HARNESS ERROR {type(e).__name__}: {e}", None
        print(f"=== cand {n}: {stem} [{comp}] -> {verdict}")
        if detail:
            print(detail)
    print(f"done: {n} candidates")


if __name__ == "__main__":
    main()

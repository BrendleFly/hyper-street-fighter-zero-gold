#!/usr/bin/env python3
"""Fast link-aware candidate tester for SFZFG ro9 - v2.

Fixes over tryc_fast.py:
  * The function's true size is read from ro9/<stem>.s (number of .word lines),
    not from the spec's SIZE field (which was silently interpreted as hex and
    could be wrong).  The spec SIZE is only used if the .s file is missing.
  * A candidate object that is SHORTER than the slot is now reported as a
    win when the bytes match AND the remaining slot bytes are all zero
    (the fixed-address linker zero-fills the gap, and the original's trailing
    padding is `nop`/zero).  The old harness silently reported these as
    failures, hiding real matches.
  * Prints a machine-readable verdict: MATCH | MATCH+PAD | NO.

Usage: python3 tryc_fast2.py <specfile>
Spec format (unchanged):
  VA <hex> / SIZE <hex> / COMP <compiler> / [FLAG ...] / END / <C source>
"""
import subprocess
import os
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

CDIR = "/home/user/sfzfg/compilers"


def _discover_compilers():
    """Map short names -> mwccps2.exe paths by scanning the compiler dir.

    Every installed build is available.  A build is named by its directory,
    e.g. "mwcps2-3.0.1b210-060308" -> key "3.0.1b210-060308", plus short
    aliases for the versions we use most.
    """
    out = {}
    if not os.path.isdir(CDIR):
        return out
    for d in sorted(os.listdir(CDIR)):
        exe = os.path.join(CDIR, d, "mwccps2.exe")
        if not os.path.exists(exe):
            continue
        if d.startswith("mwcps2-"):
            out[d[len("mwcps2-"):]] = exe
            out[d] = exe
    aliases = {
        "2.4": "2.4-001213",
        "3.0": "3.0b38",
        "3.0b38": "3.0b38",
        "3.0b50": "3.0b50-030527",
        "3.0b52": "3.0b52-030722",
        "3.0.1": "3.0.1-020123",
        "3.0.1b44": "3.0.1b44-030325",
        "3.0.1b51": "3.0.1b51-030512",
        "3.0.1b74": "3.0.1b74-030811",
        "3.0.1b75": "3.0.1b75-030916",
        "3.0.1b87": "3.0.1b87-031208",
        "3.0.1b95": "3.0.1b95-040309",
        "3.0.1b103": "3.0.1b103-040528",
        "3.0.1b119": "3.0.1b119-040914",
        "3.0.1b145": "3.0.1b145-050209",
        "3.0.1b151": "3.0.1b151-050317",
        "3.0.1b198": "3.0.1b198-051011",
        "3.0.1b205": "3.0.1b205-051227",
        "3.0.1b210": "3.0.1b210-060308",
        "3.0.3": "3.0.3-020716",
        "2.3.3": "2.3.3-000906",
        "3.0-011126": "3.0-011126",
    }
    for k, v in aliases.items():
        if v in out:
            out[k] = out[v]
    return out


MWS = _discover_compilers()
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]


def true_size(stem):
    """Real slot size of the function, in bytes, from the split .s file."""
    p = f"{ROOT}/ro9/{stem}.s"
    if not os.path.exists(p):
        return None
    n = sum(1 for l in open(p) if l.strip().startswith(".word"))
    return n * 4


def undefined_symbols(obj):
    r = subprocess.run(["mipsel-linux-gnu-nm", "-u", obj], capture_output=True, text=True)
    syms = []
    for line in r.stdout.splitlines():
        parts = line.split()
        if parts and parts[-1].startswith("func_"):
            syms.append(parts[-1])
    return syms


def sym_addr(name):
    try:
        return int(name[5:], 16)
    except ValueError:
        return 0


def test(va, size, comp, flags, src):
    # PID-unique temp names: concurrent tester runs (agents + generator)
    # must not clobber each other's objects.
    tf = f"/tmp/fcand{os.getpid()}"
    open(tf + ".c", "w").write(src)
    o = tf + ".o"
    if os.path.exists(o):
        os.remove(o)
    cf = list(CFLAGS)
    if flags:
        cf = [f for f in cf if not f.startswith("-O")] + flags
    r = subprocess.run([WIBO, MWS.get(comp, MWS["2.4"])] + cf + ["-o", o, tf + ".c"],
                       capture_output=True, text=True)
    if not os.path.exists(o):
        return "COMPILE FAIL", None, src
    defs = []
    for s in undefined_symbols(o):
        defs += ["--defsym", f"{s}=0x{sym_addr(s):x}"]
    script = tf + ".ld"
    open(script, "w").write(
        f"SECTIONS {{ . = 0x{va:08X}; .text : {{ {o}(.text) }} }}\n")
    lr = subprocess.run(["mipsel-linux-gnu-ld", "-T", script, "-o", tf + ".elf"] + defs,
                        capture_output=True, text=True)
    if lr.returncode:
        return "LINK FAIL", None, src
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", tf + ".elf", tf + ".bin"],
                   check=False)
    got = open(tf + ".bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
    if len(got) <= size and got == tgt[:len(got)]:
        tail = tgt[len(got):size]
        if not any(tail):
            return ("MATCH" if len(got) == size else "MATCH+PAD"), None, src
    gl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(got, va)]
    tl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(tgt, va)]
    diff = []
    for i in range(max(len(gl), len(tl))):
        g = gl[i] if i < len(gl) else "-"
        t = tl[i] if i < len(tl) else "-"
        if g != t:
            diff.append(f"    * {g:<34} | {t}")
    n = sum(1 for x, y in zip(got, tgt) if x != y)
    return f"NO ({n} bytes differ, {len(got)}B vs {size}B)", "\n".join(diff[:8]), src


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
        if va is None:
            continue
        ts = true_size(f"func_{va:08X}")
        if ts:
            size = ts
        if size is None:
            continue
        n += 1
        try:
            verdict, detail, _ = test(va, size, comp, flags, src)
        except Exception as e:
            verdict, detail = f"ERROR {type(e).__name__}: {e}", None
        print(f"=== cand {n}: func_{va:08X} [{comp}] -> {verdict}")
        if detail:
            print(detail)
    print(f"done: {n} candidates")


if __name__ == "__main__":
    main()

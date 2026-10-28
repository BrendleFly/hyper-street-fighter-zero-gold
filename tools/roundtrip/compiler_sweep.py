#!/usr/bin/env python3
"""Sweep every installed mwccps2 build over a set of candidates.

Two modes:

  regression  - re-test the ALREADY MATCHED functions in src_ro9/ with every
                compiler build, to find out which builds reproduce the
                original.  A build that matches everything the current
                compiler matches is a candidate for replacing it.

  probes      - test the newly discovered argument-home-slot family against
                every build, to find the build whose frame layout matches
                the original.

Usage:
  python3 compiler_sweep.py regression [sample_count]
  python3 compiler_sweep.py probes
"""
import glob
import os
import subprocess
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
SRC = f"{ROOT}/src_ro9"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]

CDIR = "/home/user/sfzfg/compilers"


def compilers():
    out = []
    for d in sorted(os.listdir(CDIR)):
        exe = f"{CDIR}/{d}/mwccps2.exe"
        if d.startswith("mwcps2-") and os.path.exists(exe):
            out.append((d[len("mwcps2-"):], exe))
    return out


def true_size(stem):
    p = f"{ROOT}/ro9/{stem}.s"
    if not os.path.exists(p):
        return None
    n = sum(1 for l in open(p) if l.strip().startswith(".word"))
    return n * 4


def undefined_symbols(obj):
    r = subprocess.run(["mipsel-linux-gnu-nm", "-u", obj], capture_output=True, text=True)
    out = []
    for line in r.stdout.splitlines():
        parts = line.split()
        if parts and parts[-1].startswith("func_"):
            out.append(parts[-1])
    return out


def sym_addr(name):
    try:
        return int(name[5:], 16)
    except ValueError:
        return 0


def try_compile(src, exe, tag):
    c = f"/tmp/{tag}.c"
    o = f"/tmp/{tag}.o"
    open(c, "w").write(src)
    if os.path.exists(o):
        os.remove(o)
    r = subprocess.run([WIBO, exe] + CFLAGS + ["-o", o, c], capture_output=True, text=True)
    if not os.path.exists(o):
        return None
    return o


def compare(va, size, obj):
    defs = []
    for s in undefined_symbols(obj):
        defs += ["--defsym", f"{s}=0x{sym_addr(s):x}"]
    script = f"/tmp/{os.path.basename(obj)}.ld"
    open(script, "w").write(
        f"SECTIONS {{ . = 0x{va:08X}; .text : {{ {obj}(.text) }} }}\n")
    lr = subprocess.run(["mipsel-linux-gnu-ld", "-T", script, "-o", f"/tmp/{os.path.basename(obj)}.elf"] + defs,
                        capture_output=True, text=True)
    if lr.returncode:
        return None
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", f"/tmp/{os.path.basename(obj)}.elf",
                    f"/tmp/{os.path.basename(obj)}.bin"], check=False)
    got = open(f"/tmp/{os.path.basename(obj)}.bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
    if len(got) <= size and got == tgt[:len(got)] and not any(tgt[len(got):size]):
        return True
    return False


def regression(sample):
    stems = []
    for l in open(f"{SRC}/matched.txt"):
        l = l.strip()
        if l:
            stems.append(l.split(":")[0].split("@")[0])
    # spread the sample across the list
    step = max(1, len(stems) // sample)
    picked = stems[::step][:sample]
    print(f"regression over {len(picked)} matched functions x {len(compilers())} compilers")
    results = {}
    for name, exe in compilers():
        ok = 0
        bad = []
        for stem in picked:
            cf = f"{SRC}/{stem}.c"
            if not os.path.exists(cf):
                continue
            va = int(stem[5:], 16)
            size = true_size(stem)
            obj = try_compile(open(cf).read(), exe, "reg")
            if obj is None:
                bad.append(f"{stem}:COMPILE")
                continue
            if compare(va, size, obj):
                ok += 1
            else:
                bad.append(stem)
        results[name] = (ok, bad)
        print(f"  {name:24s} {ok:3d}/{len(picked)}   first failures: {bad[:6]}")
    best = sorted(results.items(), key=lambda e: -e[1][0])
    print("\nBEST:", best[0][0], best[0][1][0], "matches")
    return results


PROBES = [
    ("func_00218510", """
extern void func_014B630();
void func_00218510(signed char *p)
{
    signed char * volatile q = p;
    q[1] = 0;
    q[2] = 0;
    q[6] = 0;
    func_014B630();
}
"""),
    ("func_00218200", """
extern void func_014B610();
void func_00218200(signed char *p)
{
    signed char * volatile q = p;
    q[2] = q[2] + 1;
    q[8] = 8;
    func_014B610();
}
"""),
    ("func_00216710", """
extern void func_00216770();
void func_00216710(signed char *p)
{
    func_00216770(p + 6, p + 7, p + 8);
    if (p) { p[2] = p[2] + 1; }
}
"""),
    ("func_00218550", """
extern void func_001CD840();
void func_00218550(signed char *p)
{
    signed char * volatile q = p;
    q[2] = q[2] + 1;
    func_001CD840(2);
}
"""),
]


def probes():
    for stem, src in PROBES:
        va = int(stem[5:], 16)
        size = true_size(stem)
        print(f"=== {stem} ({size}B)")
        for name, exe in compilers():
            obj = try_compile(src, exe, "pb")
            if obj is None:
                print(f"   {name:24s} COMPILE FAIL")
                continue
            r = compare(va, size, obj)
            if r:
                print(f"   {name:24s} *** MATCH ***")
            else:
                binp = f"/tmp/{os.path.basename(obj)}.bin"
                got = open(binp, "rb").read() if os.path.exists(binp) else b""
                tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
                n = sum(1 for a, b in zip(got, tgt) if a != b)
                print(f"   {name:24s} no ({n} bytes differ, {len(got)}B/{size}B)")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "probes"
    if mode == "regression":
        regression(int(sys.argv[2]) if len(sys.argv) > 2 else 30)
    else:
        probes()

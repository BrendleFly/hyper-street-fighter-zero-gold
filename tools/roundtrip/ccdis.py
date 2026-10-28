#!/usr/bin/env python3
"""Compile a C snippet with a chosen mwccps2 build and show the disassembly
side-by-side with the ORIGINAL bytes at a VA.

Usage: python3 ccdis.py <va_hex> <cfile> [compiler] [optflags...]
"""
import subprocess
import os
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
CDIR = "/home/user/sfzfg/compilers"
WIBO = "/home/user/sfzfg/tools/wibo"
BASE_CFLAGS = ["-gccinc", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]


def discover():
    """Every installed mwccps2 build, by directory name plus short aliases."""
    out = {}
    for d in sorted(os.listdir(CDIR)):
        exe = f"{CDIR}/{d}/mwccps2.exe"
        if d.startswith("mwcps2-") and os.path.exists(exe):
            out[d[len("mwcps2-"):]] = exe
            out[d] = exe
    for k, v in {"2.4": "2.4-001213", "3.0": "3.0b38", "3.0b52": "3.0b52-030722",
                 "3.0.3": "3.0.3-020716", "3.0.1b210": "3.0.1b210-060308",
                 "3.0.1b151": "3.0.1b151-050317", "3.0.1b198": "3.0.1b198-051011",
                 "3.0.1b205": "3.0.1b205-051227", "3.0b50": "3.0b50-030527",
                 "2.3.3": "2.3.3-000906", "3.0.1b44": "3.0.1b44-030325",
                 "3.0.1b51": "3.0.1b51-030512", "3.0.1b74": "3.0.1b74-030811",
                 "3.0.1b75": "3.0.1b75-030916", "3.0.1b87": "3.0.1b87-031208",
                 "3.0.1b95": "3.0.1b95-040309", "3.0.1b103": "3.0.1b103-040528",
                 "3.0.1b119": "3.0.1b119-040914", "3.0.1b145": "3.0.1b145-050209",
                 "3.0-011126": "3.0-011126", "3.0.1-020123": "3.0.1-020123"}.items():
        if v in out:
            out[k] = out[v]
    return out


MWS = discover()


def build(src, comp="2.4", opt=None, tag="cc"):
    exe = MWS.get(comp)
    if exe is None:
        return None, f"unknown compiler {comp!r} (known: {', '.join(sorted(set(MWS)))})"
    open(f"/tmp/{tag}.c", "w").write(src)
    o = f"/tmp/{tag}.o"
    if os.path.exists(o):
        os.remove(o)
    cf = list(BASE_CFLAGS)
    if opt is None:
        opt = ["-O1"]
    else:
        if not any(x.startswith("-O") for x in opt):
            opt = ["-O1"] + list(opt)
    r = subprocess.run([WIBO, exe] + cf + opt + ["-o", o, f"/tmp/{tag}.c"],
                       capture_output=True, text=True)
    if not os.path.exists(o):
        return None, (r.stdout + r.stderr)[:2000]
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o,
                    f"/tmp/{tag}.bin"], check=False)
    return open(f"/tmp/{tag}.bin", "rb").read(), None


def dis(b, va):
    return [f"{i.address:08X}: {i.bytes.hex():<10} {i.mnemonic:<8} {i.op_str}" for i in md.disasm(b, va)]


def show(va, src, comp="2.4", opt=None, size=None, tag="cc"):
    got, err = build(src, comp, opt, tag)
    if got is None:
        print("COMPILE FAIL:", err)
        return
    tgt = img[va - 0x1F0000: va - 0x1F0000 + (size if size else len(got))]
    print(f"--- got {len(got)}B  target {len(tgt)}B  comp={comp} opt={opt}")
    gl = dis(got, va)
    tl = dis(tgt, va)
    for i in range(max(len(gl), len(tl))):
        g = gl[i] if i < len(gl) else "-"
        t = tl[i] if i < len(tl) else "-"
        mark = " " if g == t else "*"
        print(f"{mark} {g:<42} | {t}")
    n = sum(1 for a, b in zip(got, tgt) if a != b)
    print(f"   -> differing bytes: {n}")


if __name__ == "__main__":
    va = int(sys.argv[1], 16)
    cf = sys.argv[2]
    comp = sys.argv[3] if len(sys.argv) > 3 else "2.4"
    opt = sys.argv[4].split(",") if len(sys.argv) > 4 else None
    show(va, open(cf).read(), comp, opt)

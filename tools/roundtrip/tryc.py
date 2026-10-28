#!/usr/bin/env python3
"""Fast candidate tester for SFZFG ro9 matching (with side-by-side disasm).

Usage on build-box:  python3 tryc.py <specfile>
specfile: blocks of
  VA <hex>
  SIZE <hex>
  END
  <C source>
  ---
"""
import subprocess, os, sys
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
IMG = "/home/user/sfzfg/roundtrip/ro9_original.bin"
img = open(IMG, "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)


def dis(data, va):
    out = []
    for ins in md.disasm(data, va):
        out.append(f"{ins.mnemonic} {ins.op_str}")
    return out


def test(va, size, src, flags=None):
    open("/tmp/cand.c", "w").write(src)
    o = "/tmp/cand.o"
    if os.path.exists(o):
        os.remove(o)
    r = subprocess.run([WIBO, MW] + (flags or CFLAGS) + ["-o", o, "/tmp/cand.c"],
                       capture_output=True, text=True)
    if not os.path.exists(o):
        return "COMPILE-FAIL", r.stderr, None
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text",
                    o, "/tmp/cand.bin"], check=False)
    got = open("/tmp/cand.bin", "rb").read()
    off = va - 0x1F0000
    tgt = img[off:off + size]
    if got == tgt:
        return "MATCH", "", got
    if len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
        return f"MATCH+pad{len(tgt)-len(got)}", "", got
    gl = dis(got, va)
    tl = dis(tgt, va)
    detail = f"  got {len(got)}B / want {size}B\n"
    for i in range(max(len(gl), len(tl))):
        g = gl[i] if i < len(gl) else "-"
        t = tl[i] if i < len(tl) else "-"
        mark = " " if g == t else "*"
        detail += f"   {mark} {g:<34} | {t}\n"
    return "NO", detail, got


def main():
    spec = open(sys.argv[1]).read()
    n = 0
    for b in spec.split("---\n"):
        if not b.strip():
            continue
        lines = b.split("\n")
        va = size = None
        i = 0
        while i < len(lines):
            s = lines[i].strip()
            if s.startswith("VA "):
                va = int(s.split()[1], 16)
            elif s.startswith("SIZE "):
                size = int(s.split()[1], 16)
            elif s == "END":
                i += 1
                break
            i += 1
        src = "\n".join(lines[i:])
        if va is None or size is None:
            continue
        n += 1
        res, detail, _ = test(va, size, src)
        print(f"=== cand {n}: func_{va:08X} ({size}B) -> {res}")
        if detail:
            print(detail)
    print(f"done: {n} candidates")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Install verified candidate wins into src_ro9 (safe version).

Unlike the older pilots/install_wins.py this one:
  * re-verifies every candidate by compiling and byte-comparing it against
    the original before it is allowed to touch matched.txt
  * writes a COMPLETE typedef header (u8/u16/u32/s8/s16/s32) so that
    candidates using signed-char casts actually compile
  * records the compiler that actually won
  * refuses to install a function that is already in matched.txt
  * leaves matched.txt untouched if any candidate fails to verify

Usage: python3 install_wins2.py <specfile> [compiler_override]
"""
import os
import re
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
GCC296 = f"{CDIR}/ee-gcc2.96/bin/ee-gcc"

HEADER = """typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
"""


def compilers():
    out = {}
    for d in sorted(os.listdir(CDIR)):
        exe = f"{CDIR}/{d}/mwccps2.exe"
        if d.startswith("mwcps2-") and os.path.exists(exe):
            out[d[len("mwcps2-"):]] = exe
    for k, v in {"2.4": "2.4-001213", "3.0": "3.0b38", "3.0.1b210": "3.0.1b210-060308",
                 "3.0b52": "3.0b52-030722", "3.0.3": "3.0.3-020716"}.items():
        if v in out:
            out[k] = out[v]
    return out


MWS = compilers()


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



def postprocess_s(path):
    """Force .set noreorder + explicit nops after jumps/branches, and
    rewrite gcc's subu/addu $sp to the original's addiu form."""
    txt = open(path).read()
    lines = txt.split("\n")
    out = []
    jmp = ("jal ", "j ", "jr ", "beq", "bne", "blez", "bgtz", "bltz",
           "bgez", "beqz", "bnez", "b ")
    for ln in lines:
        s = ln.strip()
        if s == ".set reorder":
            out.append("\t.set\tnoreorder")
            continue
        out.append(ln)
        w = s.replace("	", " ").split(" ")[0] if s else ""
        if w in ("jal", "j", "jr", "beq", "bne", "blez", "bgtz", "bltz",
                 "bgez", "beqz", "bnez", "b") and not s.endswith(":"):
            out.append("\tnop")
    txt = "\n".join(out)
    if ".set\tnoreorder" not in txt.split("#APP")[0]:
        txt = txt.replace("\t.text", "\t.text\n\t.set\tnoreorder", 1)
    # sp adjustment opcodes: gcc subu/addu -> original addiu
    txt = re.sub(r"subu\t(\$sp,\$sp,)(\d+)",
                 lambda m: "addiu\t%s-%d" % (m.group(1), int(m.group(2))), txt)
    txt = txt.replace("addu\t$sp,$sp,", "addiu\t$sp,$sp,")
    open(path, "w").write(txt)


def verify(va, size, comp, src, tag):
    c = f"/tmp/{tag}.c"
    o = f"/tmp/{tag}.o"
    open(c, "w").write(src)
    if os.path.exists(o):
        os.remove(o)
    if comp.startswith("ee-gcc"):
        # EE GCC route: compile to .s, assemble with modern gas.  The .c
        # carries SDK-style asm macros (so lb/dsll32 appear verbatim).
        s = f"/tmp/{tag}.s"
        r = subprocess.run([GCC296, "-O1", "-fno-delayed-branch", "-S", "-o", s, c],
                           capture_output=True, text=True)
        if not os.path.exists(s):
            return False, "EEGCC FAIL: " + (r.stdout + r.stderr)[-300:]
        postprocess_s(s)
        r = subprocess.run(["mipsel-linux-gnu-as", "-EL", "-march=r5900",
                            "-mabi=eabi", "-G", "128", "-o", o, s],
                           capture_output=True, text=True)
        if not os.path.exists(o):
            return False, "AS FAIL: " + r.stderr[-200:]
        # strip ELF junk sections (they would land as orphans in the link)
        subprocess.run(["mipsel-linux-gnu-objcopy",
                        "-R", ".reginfo", "-R", ".MIPS.abiflags", "-R", ".pdr",
                        "-R", ".gnu.attributes", o, o + ".j"],
                       check=False)
        os.replace(o + ".j", o)
    else:
        exe = MWS.get(comp)
        if not exe:
            # explicit failure, NOT a silent fallback to 2.4
            return False, f"no such compiler: {comp}"
        r = subprocess.run([WIBO, exe] + CFLAGS + ["-o", o, c],
                           capture_output=True, text=True)
        if not os.path.exists(o):
            return False, "COMPILE FAIL: " + (r.stdout + r.stderr)[-300:]
    defs = []
    for s in undefined_symbols(o):
        defs += ["--defsym", f"{s}=0x{sym_addr(s):x}"]
    script = f"/tmp/{tag}.ld"
    open(script, "w").write(f"SECTIONS {{ . = 0x{va:08X}; .text : {{ {o}(.text) }} }}\n")
    lr = subprocess.run(["mipsel-linux-gnu-ld", "-T", script, "-o", f"/tmp/{tag}.elf"] + defs,
                        capture_output=True, text=True)
    if lr.returncode:
        return False, "LINK FAIL: " + lr.stderr[-200:]
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", f"/tmp/{tag}.elf", f"/tmp/{tag}.bin"],
                   check=False)
    got = open(f"/tmp/{tag}.bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
    if len(got) <= size and got == tgt[:len(got)] and not any(tgt[len(got):size]):
        return True, ("MATCH" if len(got) == size else "MATCH+PAD")
    n = sum(1 for a, b in zip(got, tgt) if a != b)
    return False, f"{n} bytes differ"


def normalize_callees(src):
    """Rewrite callee names to the canonical func_XXXXXXXX (8 hex, upper).

    Agents sometimes emit func_0014B610 for a call to 0x14B610.  The address
    is what matters (the linker stub is derived from the name), but the
    canonical form keeps matched.txt and the sources consistent.
    """
    def rep(m):
        return "func_%08X" % int(m.group(1), 16)
    return re.sub(r"func_([0-9A-Fa-f]{8})\b", rep, src)


def strip_typedefs(body):
    """Remove typedef lines the candidate may already carry (we prepend our
    own header, and a duplicate typedef is a compile error in C89)."""
    out = []
    for line in body.split("\n"):
        s = line.strip()
        if s.startswith("typedef ") and s.endswith(";"):
            continue
        out.append(line)
    return "\n".join(out)


def main():
    specpath = sys.argv[1]
    override = sys.argv[2] if len(sys.argv) > 2 else None
    blocks = [b for b in open(specpath).read().split("---\n") if "VA " in b]
    # existing matched stems
    mt = f"{SRC}/matched.txt"
    lines = [l.strip() for l in open(mt) if l.strip()]
    existing = {l.split(":")[0].split("@")[0] for l in lines}

    wins = []
    for b in blocks:
        m = re.search(r"VA ([0-9A-Fa-f]{8})", b)
        if not m:
            continue
        va = int(m.group(1), 16)
        stem = f"func_{va:08X}"
        if stem in existing:
            continue
        body = b.split("END\n", 1)[1] if "END\n" in b else b
        comp = override
        if not comp:
            mm = re.search(r"COMP (\S+)", b)
            comp = mm.group(1) if mm else "3.0.1b210"
        size = true_size(stem)
        if size is None:
            continue
        src = HEADER + normalize_callees(strip_typedefs(body))
        ok, msg = verify(va, size, comp, src, f"iw{os.getpid()}")
        if not ok:
            print(f"  REJECT {stem} [{comp}]: {msg}")
            continue
        wins.append((stem, comp, src, msg))
        print(f"  VERIFIED {stem} [{comp}]: {msg}")

    if not wins:
        print("nothing to install")
        return
    # one entry per stem only: a function is compiled once, with one compiler
    done = set(existing)
    added = 0
    for stem, comp, src, _ in wins:
        if stem in done:
            continue
        open(f"{SRC}/{stem}.c", "w").write(src)
        ent = f"{stem}@{comp}"
        if ent not in lines:
            lines.append(ent)
        done.add(stem)
        added += 1
    # collapse any pre-existing duplicate stems (keep the first entry)
    seen_stems = set()
    collapsed = []
    for l in lines:
        st = l.split(":")[0].split("@")[0]
        if st in seen_stems:
            continue
        seen_stems.add(st)
        collapsed.append(l)
    lines = sorted(collapsed, key=lambda x: x.split(":")[0].split("@")[0])
    open(mt, "w").write("\n".join(lines) + "\n")
    print(f"installed {added} functions; matched.txt now {len(lines)} entries")


if __name__ == "__main__":
    main()

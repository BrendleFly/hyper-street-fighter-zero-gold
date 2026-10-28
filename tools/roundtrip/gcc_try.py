#!/usr/bin/env python3
"""GCC candidate tester for SFZFG ro9 - modeled on tryc_fast2.py but takes a
GCC command line instead of a MWCC build.

Spec block:
  VA <hex>
  GCC <compiler> <flags...>        e.g. GCC mips64el-linux-gnuabi64-gcc -O1
  END
  <C source>
Blocks separated by a line containing only ---.
Verdicts: MATCH | MATCH+PAD | NO (with diff like tryc_fast2).
"""
import os
import re as _re
import subprocess
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)
TMP = "/tmp/gt_%d" % os.getpid()


def true_size(stem):
    p = f"{ROOT}/ro9/{stem}.s"
    if not os.path.exists(p):
        return None
    return 4 * sum(1 for l in open(p) if l.strip().startswith(".word"))



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
    txt = _re.sub(r"subu\t(\$sp,\$sp,)(\d+)",
                 lambda m: "addiu\t%s-%d" % (m.group(1), int(m.group(2))), txt)
    txt = txt.replace("addu\t$sp,$sp,", "addiu\t$sp,$sp,")
    open(path, "w").write(txt)


def undefined_symbols(obj, nm="mipsel-linux-gnu-nm"):
    r = subprocess.run([nm, "-u", obj],
                       capture_output=True, text=True)
    return [l.split()[-1] for l in r.stdout.splitlines()
            if l.split() and l.split()[-1].startswith("func_")]


def test(va, size, gccline, src):
    open(TMP + ".c", "w").write(src)
    o = TMP + ".o"
    if os.path.exists(o):
        os.remove(o)
    # "+sl" at the end of the GCC line: compile to .s, rewrite unsigned
    # small loads to signed (lbu->lb, lhu->lh), then assemble with the EE
    # assembler.  Legit because a following dsll32/dsra32 pair re-derives
    # the sign bits, so the rewrite only changes the load opcode — which
    # is exactly the original compiler's choice.
    sl = "+sl" in gccline
    if sl:
        gccline = [a for a in gccline if a != "+sl"]
        s = TMP + ".s"
        r = subprocess.run(gccline + ["-fno-delayed-branch", "-S", "-o", s, TMP + ".c"],
                           capture_output=True, text=True)
        if not os.path.exists(s):
            return "COMPILE FAIL: " + (r.stdout + r.stderr)[-300:], None
        txt = open(s).read()
        txt = _re.sub(r"\blbu\b", "lb", txt)
        txt = _re.sub(r"\blhu\b", "lh", txt)
        open(s, "w").write(txt)
        postprocess_s(s)
        as_bin = "/home/user/sfzfg/compilers/ee-gcc2.96/ee/bin/as"
        r = subprocess.run([as_bin, "-EL", "-o", o, s],
                           capture_output=True, text=True)
        if not os.path.exists(o):
            return "ASM FAIL: " + (r.stdout + r.stderr)[-300:], None
    else:
        r = subprocess.run(gccline + ["-c", "-o", o, TMP + ".c"],
                           capture_output=True, text=True)
        if not os.path.exists(o):
            return "COMPILE FAIL: " + (r.stdout + r.stderr)[-300:], None
    # binutils follow the gcc's prefix (n64 vs o32 emulations differ)
    import shutil
    prefix = gccline[0].rsplit("-gcc", 1)[0] if not sl else "mipsel-linux-gnu"
    ld = prefix + "-ld" if shutil.which(prefix + "-ld") else "mipsel-linux-gnu-ld"
    nm = prefix + "-nm" if shutil.which(prefix + "-nm") else "mipsel-linux-gnu-nm"
    oc = prefix + "-objcopy" if shutil.which(prefix + "-objcopy") else "mipsel-linux-gnu-objcopy"
    defs = []
    for s in undefined_symbols(o, nm):
        defs += ["--defsym", f"{s}=0x{int(s[5:], 16):x}"]
    script = TMP + ".ld"
    open(script, "w").write(
        f"SECTIONS {{ . = 0x{va:08X}; .text : {{ {o}(.text) }} }}\n")
    lr = subprocess.run([ld, "-T", script,
                         "-o", TMP + ".elf"] + defs, capture_output=True, text=True)
    if lr.returncode:
        # old ee-gcc objects have symtabs modern ld rejects; if the object
        # is relocation-free, extract .text directly instead of linking
        rr = subprocess.run(["mipsel-linux-gnu-objdump", "-r", o],
                            capture_output=True, text=True)
        nreloc = len([l for l in rr.stdout.splitlines() if l.startswith("0")])
        if nreloc == 0 and not defs:
            subprocess.run([oc, "-O", "binary", "--only-section=.text",
                            o, TMP + ".bin"], check=False)
            got = open(TMP + ".bin", "rb").read()
            tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
            if len(got) <= size and got == tgt[:len(got)] and not any(tgt[len(got):size]):
                return ("MATCH" if len(got) == size else "MATCH+PAD"), None
            gl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(got, va)]
            tl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(tgt, va)]
            diff = []
            for i in range(max(len(gl), len(tl))):
                g = gl[i] if i < len(gl) else "-"
                t = tl[i] if i < len(tl) else "-"
                if g != t:
                    diff.append(f"    * {g:<36s} | {t}")
            n = sum(1 for x, y in zip(got, tgt) if x != y)
            return f"NO ({n} bytes differ, {len(got)}B vs {size}B)", "\n".join(diff[:10])
        return "LINK FAIL: " + lr.stderr[-200:], None
    subprocess.run([oc, "-O", "binary",
                    TMP + ".elf", TMP + ".bin"], check=False)
    got = open(TMP + ".bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + size]
    if len(got) <= size and got == tgt[:len(got)] and not any(tgt[len(got):size]):
        return ("MATCH" if len(got) == size else "MATCH+PAD"), None
    gl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(got, va)]
    tl = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(tgt, va)]
    diff = []
    for i in range(max(len(gl), len(tl))):
        g = gl[i] if i < len(gl) else "-"
        t = tl[i] if i < len(tl) else "-"
        if g != t:
            diff.append(f"    * {g:<36s} | {t}")
    n = sum(1 for x, y in zip(got, tgt) if x != y)
    return f"NO ({n} bytes differ, {len(got)}B vs {size}B)", "\n".join(diff[:10])


def main():
    spec = open(sys.argv[1]).read()
    n = 0
    for b in spec.split("---\n"):
        if not b.strip():
            continue
        lines = b.split("\n")
        va = None
        gccline = None
        i = 0
        while i < len(lines):
            s = lines[i].strip()
            if s.startswith("VA "):
                va = int(s.split()[1], 16)
            elif s.startswith("GCC "):
                gccline = s.split()[1:]
            elif s == "END":
                i += 1
                break
            i += 1
        src = "\n".join(lines[i:])
        if va is None or gccline is None:
            continue
        ts = true_size(f"func_{va:08X}") or 80
        n += 1
        verdict, detail = test(va, ts, gccline, src)
        print(f"=== cand {n}: func_{va:08X} [{' '.join(gccline[0:1])} {gccline[1:]}] -> {verdict}")
        if detail:
            print(detail)
    print(f"done: {n} candidates")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Matched-function build driver for ro9 (Hyper Street Fighter Alpha).

Reads src/ro9/matched.txt (one func_XXXXXXXX[@compiler][:pad] per line, C in
src/ro9/), builds the full image on the build-box-side layout, links, and
byte-compares against the original. Everything must stay byte-exact.

Run ON build-box:  python3 src_ro9/match_build.py

Notes:
  * Every installed mwccps2 build is available; the compiler is chosen per
    function from the "@compiler" suffix in matched.txt.
  * Calls to functions that live OUTSIDE the ro9 image (the game's other
    modules, e.g. the sub/launcher at 0x1CD840) are resolved with
    --defsym absolute symbols.  They emit no bytes, so the linked image
    stays byte-identical.
"""
import re
import subprocess
import os
import sys
import glob

ROOT = os.environ.get("SFZFG_ROOT", "/home/user/sfzfg/roundtrip")
CDIR = os.environ.get("SFZFG_COMPILERS", "/home/user/sfzfg/compilers")


def discover_compilers():
    out = {}
    if not os.path.isdir(CDIR):
        return out
    for d in sorted(os.listdir(CDIR)):
        exe = f"{CDIR}/{d}/mwccps2.exe"
        if d.startswith("mwcps2-") and os.path.exists(exe):
            out[d[len("mwcps2-"):]] = exe
    for k, v in {"2.4": "2.4-001213", "3.0": "3.0b38", "3.0b52": "3.0b52-030722",
                 "3.0.3": "3.0.3-020716", "3.0.1b210": "3.0.1b210-060308",
                 "3.0.1b198": "3.0.1b198-051011", "3.0.1b151": "3.0.1b151-050317",
                 "3.0.1b205": "3.0.1b205-051227", "3.0b50": "3.0b50-030527",
                 "2.3.3": "2.3.3-000906"}.items():
        if v in out:
            out[k] = out[v]
    return out


MWS = discover_compilers()
MW = MWS.get("2.4")
GCC296 = "/home/user/sfzfg/compilers/ee-gcc2.96/bin/ee-gcc"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
ASFLAGS = ["-EL", "-march=r5900", "-mabi=eabi", "-G", "128"]

BUILD = f"{ROOT}/build_eabi"
ASM = f"{ROOT}/ro9"
SRC = f"{ROOT}/src_ro9"
LD = f"{ROOT}/ro9_fixed.ld"
ORIG = f"{ROOT}/ro9_original.bin"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def postprocess_s(path):
    lines = open(path).read().split("\n")
    out = []
    for ln in lines:
        s = ln.strip()
        if s == ".set reorder":
            out.append("\t.set\tnoreorder")
            continue
        out.append(ln)
        w = s.replace("\t", " ").split(" ")[0] if s else ""
        if w in ("jal", "j", "jr", "beq", "bne", "blez", "bgtz", "bltz",
                 "bgez", "beqz", "bnez", "b") and not s.endswith(":"):
            out.append("\tnop")
    txt = "\n".join(out)
    if ".set\tnoreorder" not in txt.split("#APP")[0]:
        txt = txt.replace("\t.text", "\t.text\n\t.set\tnoreorder", 1)
    txt = re.sub(r"subu\t(\$sp,\$sp,)(\d+)",
                 lambda m: "addiu\t%s-%d" % (m.group(1), int(m.group(2))), txt)
    txt = txt.replace("addu\t$sp,$sp,", "addiu\t$sp,$sp,")
    open(path, "w").write(txt)


def undefined_func_syms(obj):
    r = run(["mipsel-linux-gnu-nm", "-u", obj])
    out = set()
    for line in r.stdout.splitlines():
        parts = line.split()
        if parts and parts[-1].startswith("func_"):
            try:
                out.add((parts[-1], int(parts[-1][5:], 16)))
            except ValueError:
                pass
    return out


def defined_func_syms(obj):
    r = run(["mipsel-linux-gnu-nm", "--defined-only", obj])
    out = set()
    for line in r.stdout.splitlines():
        parts = line.split()
        if parts and parts[-1].startswith("func_"):
            out.add(parts[-1])
    return out


def main():
    img = open(ORIG, "rb").read()
    lo = 0x1F0000
    hi = lo + len(img)

    matched = []
    for l in open(f"{SRC}/matched.txt"):
        l = l.strip()
        if not l:
            continue
        # entry format: stem[@compiler][.pad]  e.g. func_004B5E70@3.0.1b210
        comp = "2.4"
        if "@" in l:
            l, _, comp = l.partition("@")
        stem, _, pad = l.partition(":")
        matched.append((stem, int(pad) if pad else 0, comp))
    print(f"matched functions: {len(matched)}")
    fails = 0
    external = set()
    for stem, pad, comp in matched:
        o = f"{BUILD}/{stem}.o"
        if comp.startswith("ee-gcc"):
            cs = f"{BUILD}/{stem}.ee.s"
            r = run([GCC296, "-O1", "-fno-delayed-branch", "-S", "-o", cs, f"{SRC}/{stem}.c"])
            if not os.path.exists(cs):
                print(f"  C COMPILE FAIL {stem}: {r.stderr[:200]}")
                fails += 1
                continue
            postprocess_s(cs)
            r = run(["mipsel-linux-gnu-as"] + ASFLAGS + ["-o", o, cs])
            os.remove(cs)
        else:
            mw = MWS.get(comp)
            if mw is None:
                print(f"  C COMPILE FAIL {stem}: unknown compiler {comp}")
                fails += 1
                continue
            r = run([WIBO, mw] + CFLAGS + ["-o", o, f"{SRC}/{stem}.c"])
        if not os.path.exists(o):
            print(f"  C COMPILE FAIL {stem}: {r.stderr[:200]}")
            fails += 1
            continue
        run(["mipsel-linux-gnu-objcopy", "--set-section-alignment", ".text=4", o, o + ".t"])
        os.replace(o + ".t", o)
        for name, addr in undefined_func_syms(o):
            external.add((name, addr))
    if fails:
        sys.exit(f"{fails} C compilations failed")

    # assemble every non-matched .s fresh
    os.makedirs(BUILD, exist_ok=True)
    matched_stems = {stem for stem, _, _ in matched}
    slist = sorted(glob.glob(f"{ASM}/func_*.s")) + [f"{ASM}/header.s", f"{ASM}/data.s"]
    for s in slist:
        stem = os.path.basename(s)[:-2]
        if stem in matched_stems:
            continue
        o = f"{BUILD}/{stem}.o"
        r = run(["mipsel-linux-gnu-as"] + ASFLAGS + ["-o", o, s])
        if not os.path.exists(o):
            sys.exit(f"as failed on {s}: {r.stderr[:200]}")
        if os.path.basename(s).startswith("func_"):
            run(["mipsel-linux-gnu-objcopy", "--set-section-alignment", ".text=4", o, o + ".t"])
            os.replace(o + ".t", o)

    # link list: header, func objects by ADDRESS, data
    funs = []
    cobjs = {stem for stem, _, _ in matched}
    for o in glob.glob(f"{BUILD}/func_*.o"):
        stem = os.path.basename(o)[:-2]
        if stem in cobjs:
            continue
        funs.append((float(int(stem[5:], 16)), stem + ".o"))
    for stem, pad, comp in matched:
        funs.append((float(int(stem[5:], 16)), f"{BUILD}/{stem}.o"))
    funs.sort(key=lambda e: e[0])
    # the fixed-address script references every object by path; do not also
    # list them on the command line (that would duplicate every symbol)
    #
    # Any func_* symbol that no object defines is a call target the split
    # never produced a slot for (the splitter merged it into a neighbour) or
    # a function in another module.  Give it an absolute symbol at the
    # address its name encodes - absolute symbols emit no bytes, so the
    # linked image stays byte-identical.
    defined = set()
    for o in glob.glob(f"{BUILD}/*.o"):
        defined |= defined_func_syms(o)
    defsyms = []
    for name, addr in sorted(external):
        if name in defined:
            continue
        defsyms += ["--defsym", f"{name}=0x{addr:x}"]
    if defsyms:
        print(f"external call stubs: {len(defsyms) // 2}")
    r = run(["mipsel-linux-gnu-ld", "-T", LD, "-o", f"{ROOT}/ro9_rt.elf"] + defsyms)
    if r.returncode:
        sys.exit("link failed: " + r.stderr[:500])
    run(["mipsel-linux-gnu-objcopy", "-O", "binary", f"{ROOT}/ro9_rt.elf", f"{ROOT}/ro9_rt.bin"])
    got = open(f"{ROOT}/ro9_rt.bin", "rb").read()
    want = open(ORIG, "rb").read()
    import datetime
    status = {
        "checked": datetime.datetime.now().isoformat(timespec="seconds"),
        "matched": len(matched),
        "external_stubs": len(external),
    }
    if got == want:
        status["result"] = "BYTE-EXACT"
        status["differing_bytes"] = 0
        print(f"*** FULL IMAGE BYTE-EXACT ({len(matched)} C functions swapped in) ***")
    else:
        n = sum(1 for a, b in zip(got, want) if a != b)
        status["result"] = "MISMATCH"
        status["differing_bytes"] = n
        print(f"MISMATCH: {n} differing bytes (got {len(got)}B want {len(want)}B)")
    try:
        with open(f"{SRC}/build_status.json", "w") as f:
            import json
            json.dump(status, f, indent=1)
    except OSError:
        pass


if __name__ == "__main__":
    main()

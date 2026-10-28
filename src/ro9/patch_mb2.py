#!/usr/bin/env python3
"""Re-add the ee-gcc route (with flag + postprocess) to the restored
match_build.py.  Run on build-box in src_ro9/."""
src = open("match_build.py").read()

# 1. constant
old = 'MW = MWS.get("2.4")'
assert old in src
src = src.replace(old, old + '\nGCC296 = "/home/user/sfzfg/compilers/ee-gcc2.96/bin/ee-gcc"')

# 2. compile loop: branch on ee-gcc, explicit unknown-compiler failure
old2 = (
    '    for stem, pad, comp in matched:\n'
    '        o = f"{BUILD}/{stem}.o"\n'
    '        mw = MWS.get(comp, MW)\n'
    '        r = run([WIBO, mw] + CFLAGS + ["-o", o, f"{SRC}/{stem}.c"])\n'
    '        if not os.path.exists(o):\n'
)
new2 = (
    '    for stem, pad, comp in matched:\n'
    '        o = f"{BUILD}/{stem}.o"\n'
    '        if comp.startswith("ee-gcc"):\n'
    '            cs = f"{BUILD}/{stem}.ee.s"\n'
    '            r = run([GCC296, "-O1", "-fno-delayed-branch", "-S", "-o", cs, f"{SRC}/{stem}.c"])\n'
    '            if not os.path.exists(cs):\n'
    '                print(f"  C COMPILE FAIL {stem}: {r.stderr[:200]}")\n'
    '                fails += 1\n'
    '                continue\n'
    '            postprocess_s(cs)\n'
    '            r = run(["mipsel-linux-gnu-as"] + ASFLAGS + ["-o", o, cs])\n'
    '            os.remove(cs)\n'
    '        else:\n'
    '            mw = MWS.get(comp)\n'
    '            if mw is None:\n'
    '                print(f"  C COMPILE FAIL {stem}: unknown compiler {comp}")\n'
    '                fails += 1\n'
    '                continue\n'
    '            r = run([WIBO, mw] + CFLAGS + ["-o", o, f"{SRC}/{stem}.c"])\n'
    '        if not os.path.exists(o):\n'
)
assert old2 in src, "loop not found"
src = src.replace(old2, new2)

# 3. postprocess function
post = '''def postprocess_s(path):
    lines = open(path).read().split("\\n")
    out = []
    for ln in lines:
        s = ln.strip()
        if s == ".set reorder":
            out.append("\\t.set\\tnoreorder")
            continue
        out.append(ln)
        w = s.replace("\\t", " ").split(" ")[0] if s else ""
        if w in ("jal", "j", "jr", "beq", "bne", "blez", "bgtz", "bltz",
                 "bgez", "beqz", "bnez", "b") and not s.endswith(":"):
            out.append("\\tnop")
    txt = "\\n".join(out)
    if ".set\\tnoreorder" not in txt.split("#APP")[0]:
        txt = txt.replace("\\t.text", "\\t.text\\n\\t.set\\tnoreorder", 1)
    txt = re.sub(r"subu\\t(\\$sp,\\$sp,)(\\d+)",
                 lambda m: "addiu\\t%s-%d" % (m.group(1), int(m.group(2))), txt)
    txt = txt.replace("addu\\t$sp,$sp,", "addiu\\t$sp,$sp,")
    open(path, "w").write(txt)


'''
anchor = "def undefined_func_syms(obj):"
assert anchor in src
src = src.replace(anchor, post + anchor)

if "\nimport re\n" not in src:
    src = src.replace("import subprocess", "import re\nimport subprocess", 1)
open("match_build.py", "w").write(src)
print("patched OK")

#!/usr/bin/env python3
"""Patch match_build.py's ee-gcc route with -fno-delayed-branch and the
noreorder/nop/addiu .s postprocessor.  Run on build-box in src_ro9/."""
import re

src = open("match_build.py").read()

old = (
    '        if comp.startswith("ee-gcc"):\n'
    '            cs = f"{BUILD}/{stem}.ee.s"\n'
    '            r = run([GCC296, "-O1", "-S", "-o", cs, f"{SRC}/{stem}.c"])\n'
)
new = (
    '        if comp.startswith("ee-gcc"):\n'
    '            cs = f"{BUILD}/{stem}.ee.s"\n'
    '            r = run([GCC296, "-O1", "-fno-delayed-branch", "-S", "-o", cs, f"{SRC}/{stem}.c"])\n'
)
assert old in src, "compile block not found"
src = src.replace(old, new)

old2 = (
    '            r = run(["mipsel-linux-gnu-as"] + ASFLAGS + ["-o", o, cs])\n'
    '            os.remove(cs)\n'
)
new2 = (
    '            postprocess_s(cs)\n'
    '            r = run(["mipsel-linux-gnu-as"] + ASFLAGS + ["-o", o, cs])\n'
    '            os.remove(cs)\n'
)
assert old2 in src, "as block not found"
src = src.replace(old2, new2)

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
assert anchor in src, "anchor not found"
src = src.replace(anchor, post + anchor)
if "\nimport re\n" not in src:
    src = src.replace("import subprocess", "import re\nimport subprocess", 1)
open("match_build.py", "w").write(src)
print("patched OK")

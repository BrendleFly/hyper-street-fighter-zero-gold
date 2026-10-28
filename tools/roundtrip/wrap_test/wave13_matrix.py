import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
va, sz = 0x00420DE0, 48
tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]

HDR = "typedef signed char s8;\ntypedef unsigned int u32;\n"
BASE_DECL = "    u32 a;\n    s8 v;\n"
PRE = "    a = 0x70000000;\n    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);\n"

ENDINGS = {
"e1": "    r = v;\n    r = v & 4;\n    a = 0x70000000;\n    *(volatile u32 *)(a + 0x1150) = r;\n",
"e2": "    r = (int)v;\n    a = 0x70000000;\n    *(volatile u32 *)(a + 0x1150) = r & 4;\n",
"e3": "    r = v;\n    a = 0x70000000;\n    *(volatile u32 *)(a + 0x1150) = r & 4;\n",
"e4": "    a = 0x70000000;\n    *(volatile u32 *)(a + 0x1150) = (int)v & 4;\n",
"e5": "    r = v & 4;\n    r = v;\n    r = r & 4;\n    a = 0x70000000;\n    *(volatile u32 *)(a + 0x1150) = r;\n",
"e6": "    r = v ? v : 0;\n    r = v & 4;\n    a = 0x70000000;\n    *(volatile u32 *)(a + 0x1150) = r;\n",
"e7": "    a = 0x70000000;\n    *(volatile u32 *)(a + 0x1150) = (v & 4) | (v & 0);\n",
"e8": "    r = v >> 0;\n    r = v & 4;\n    a = 0x70000000;\n    *(volatile u32 *)(a + 0x1150) = r;\n",
}

def test(tag, src, opt):
    open(f"/tmp/w13_{tag}.c", "w").write(src)
    o = f"/tmp/w13_{tag}.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW, "-gccinc"] + opt + ["-c", "-lang", "c", "-str", "readonly",
                   "-sdatathreshold", "0", "-o", o, f"/tmp/w13_{tag}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{tag} {opt}: compile fail")
        return False
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin", "rb").read()
    if got == tgt:
        print(f"*** {tag} {opt}: FULL MATCH ***")
        return True
    if len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
        print(f"*** {tag} {opt}: MATCH + {len(tgt)-len(got)}B pad ***")
        return True
    w0 = got[:4].hex() if got else "----"
    nw = sum(1 for i in range(0, min(len(got), len(tgt)), 4) if got[i:i+4] == tgt[i:i+4])
    print(f"    {tag} {opt}: no (got {len(got)}B, w0={w0}, words {nw}/{len(tgt)//4})")
    return False

for tag, end in ENDINGS.items():
    src = HDR + "void func_00420DE0(void)\n{\n    u32 a;\n    s8 v;\n    int r;\n" + PRE + end + "}\n"
    test(tag, src, ["-O1"])

# char (plain) variant of the base shape
src_char = ("typedef unsigned int u32;\n"
            "void func_00420DE0(void)\n{\n    u32 a;\n    char v;\n" + PRE +
            "    int r;\n    r = v & 4;\n    a = 0x70000000;\n    *(volatile u32 *)(a + 0x1150) = r;\n}\n")
test("char_plain", src_char, ["-O1"])

# opt keyword guesses on the base v2 shape
V2 = HDR + "void func_00420DE0(void)\n{\n    u32 a;\n    s8 v;\n    int r;\n" + PRE + \
     "    r = v & 4;\n    a = 0x70000000;\n    *(volatile u32 *)(a + 0x1150) = r;\n}\n"
for extra in (["-opt", "level=1,nodead"], ["-opt", "level=1,nodce"], ["-opt", "nodeadcode"],
              ["-opt", "level=1,nodeadcode"], ["-inline", "noauto"], ["-fp", "off"]):
    tag = "opt_" + "_".join(extra).replace("=", "_").replace(",", "_")
    test(tag, V2, ["-O1"] + extra)

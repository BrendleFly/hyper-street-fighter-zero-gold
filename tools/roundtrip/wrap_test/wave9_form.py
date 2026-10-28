import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
BASE = ["-gccinc", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
os.makedirs("w9", exist_ok=True)

def body(va, n):
    return img[va - 0x1F0000: va - 0x1F0000 + n]

CASES = [
    ("x23", 0x002556D0, 32, ["-O1"], """typedef unsigned char u8;
typedef unsigned int u32;
void func_002556D0(void)
{
    u32 a;
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0x3c) = 0;
}
"""),
    ("x7", 0x0051AC80, 32, ["-O1"], """typedef unsigned char u8;
typedef unsigned int u32;
void func_0051AC80(void)
{
    u32 a;
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 4) = 4;
}
"""),
    ("x34_A1", 0x00235A00, 48, ["-O1"], """typedef unsigned int u32;
void func_00235A00(void)
{
    u32 a, v;
    v = 1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v;
}
"""),
    ("x34_A1_O2", 0x00235A00, 48, ["-O2"], "SAME_AS_A1"),
    ("x34_A1_O3", 0x00235A00, 48, ["-O3"], "SAME_AS_A1"),
    ("x34_A4", 0x00235A00, 48, ["-O1"], """typedef unsigned int u32;
void func_00235A00(void)
{
    u32 a, v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    v = 1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v;
}
"""),
]

a1_src = CASES[2][4]
for tag, va, sz, opt, src in CASES:
    if src == "SAME_AS_A1":
        src = a1_src.replace("func_00235A00", f"func_{va:08X}")
    else:
        src = src.replace("func_00235A00", f"func_{va:08X}").replace(f"func_{va:08X}", f"func_{va:08X}")
    open(f"w9/{tag}.c", "w").write(src)
    o = f"/tmp/w9_{tag}.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([ "/home/user/sfzfg/tools/wibo", MW] + opt + BASE[1:] + ["-o", o, f"w9/{tag}.c"],
                   capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{tag}: COMPILE FAIL")
        continue
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin", "rb").read()
    tgt = body(va, sz)
    if got == tgt:
        print(f"*** {tag}: FULL MATCH ***")
        continue
    pre = tgt[:len(got)] == got if len(got) <= len(tgt) else False
    print(f"--- {tag}: size {len(got)} vs {sz} prefix_ok={pre}")
    for i in range(0, min(len(got), len(tgt)), 4):
        g, t = got[i:i+4].hex(), tgt[i:i+4].hex()
        if g != t:
            print(f"    word {i//4}: got {g} want {t}")

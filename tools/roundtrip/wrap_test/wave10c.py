import subprocess, os
MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
va, sz = 0x00420DE0, 48
tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]
shapes = {
"onestmt": """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    *(volatile u32 *)0x70001150 = *(volatile s8 *)(*(volatile u32 *)0x70001118 + 0x370) & 4;
}
""",
"onestmt_a": """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370) & 4;
}
""",
"uchar": """typedef unsigned char u8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a;
    u8 v;
    a = 0x70000000;
    v = *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = (u32)(s32) * (volatile s8 *)&v & 4;
}
""",
"uchar2": """typedef signed char s8;
typedef unsigned char u8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a;
    u8 v;
    s8 sv;
    a = 0x70000000;
    v = *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    sv = (s8)v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = sv & 4;
}
""",
}
for opt in (["-O1"], ["-O1,p"]):
    for tag, s in shapes.items():
        open("/tmp/py.c", "w").write(s)
        o = "/tmp/py.o"
        if os.path.exists(o):
            os.remove(o)
        subprocess.run([WIBO, MW, "-gccinc"] + opt + ["-c", "-lang", "c", "-str", "readonly",
                       "-sdatathreshold", "0", "-o", o, "/tmp/py.c"], capture_output=True, text=True)
        if not os.path.exists(o):
            print(f"{opt} {tag}: compile fail")
            continue
        subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
        got = open("/tmp/g.bin", "rb").read()
        if got == tgt:
            print(f"*** MATCH {opt} {tag} exact")
        elif len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
            print(f"*** MATCH {opt} {tag} +{len(tgt)-len(got)}B pad")
        else:
            w0 = got[:4].hex() if got else "----"
            print(f"    {opt} {tag}: no (got " + str(len(got)) + "B, w0=" + w0 + ")")

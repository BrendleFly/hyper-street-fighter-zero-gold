import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()

def test(tag, va, sz, src):
    open(f"/tmp/{tag}.c", "w").write(src)
    o = f"/tmp/{tag}.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"/tmp/{tag}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{tag}: COMPILE FAIL")
        return
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]
    if got == tgt:
        print(f"*** {tag}: FULL MATCH ***")
    elif len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
        print(f"*** {tag}: MATCH + {len(tgt)-len(got)}B pad ***")
    else:
        g0 = got[:4].hex() if got else "----"
        print(f"--- {tag}: mismatch, word0={g0} (want 0070033c), len {len(got)} vs {sz}")

# 420DE0 variant B: v declared first
test("vB1", 0x00420DE0, 48, """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    s8 v;
    u32 a;

    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v & 4;
}
""")

# 420DE0 variant C: single var a reused for the value too
test("vC1", 0x00420DE0, 48, """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    s8 v;
    u32 a;

    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v & 4;
    (void)a;
}
""")

# 420DE0 variant D: explicit int temp r for the store value
test("vD1", 0x00420DE0, 48, """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a;
    s8 v;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    v = *(volatile s8 *)(a + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v & 4;
}
""")

# 420DE0 variant E: v declared before a, reassignment idiom
test("vE1", 0x00420DE0, 48, """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    s8 v;
    u32 a;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    v = *(volatile s8 *)(a + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v & 4;
}
""")

# A910 variant: same as matched x7/x8 style, s16 w after andi
test("aB1", 0x0036A910, 80, """typedef signed char s8;
typedef signed short s16;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
void func_0036A910(void)
{
    s8 b;
    s16 w;
    u32 a;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    b = *(volatile s8 *)(a + 0x379);
    a = 0x70000000;
    *(volatile u8 *)(a + 0x1124) = b;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    w = *(volatile s16 *)(a + 0x1124);
    w &= 0x77;
    *(volatile u16 *)(a + 0x1124) = w;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = w;
}
""")

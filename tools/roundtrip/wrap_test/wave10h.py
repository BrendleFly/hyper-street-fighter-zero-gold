import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()

def run(tag, va, sz, src):
    open(f"/home/user/sfzfg/roundtrip/pilots/{tag}.c", "w").write(src)
    o = f"/tmp/{tag}.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"/home/user/sfzfg/roundtrip/pilots/{tag}.c"],
                   capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{tag}: COMPILE FAIL")
        return False
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]
    if got == tgt:
        print(f"*** {tag}: FULL MATCH ***")
        return True
    elif len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
        print(f"*** {tag}: MATCH + {len(tgt)-len(got)}B pad ***")
        return True
    else:
        w0 = got[:4].hex() if got else "----"
        print(f"--- {tag}: no (got {len(got)}B vs {sz}B, w0={w0})")
        return False

# 420DE0 with dead int temp (explains the dead dsll/dsra pair)
run("d_420", 0x00420DE0, 48, """typedef signed char s8;
typedef signed int s32;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a;
    s8 v;
    s32 t;

    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    t = v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v & 4;
}
""")

# A910 with the two dead int temps (matches the dsll/dsra chain)
run("d_A910", 0x0036A910, 80, """typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
void func_0036A910(void)
{
    u32 a;
    s8 b;
    s16 w;
    s32 t1;
    s32 t2;

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
    t1 = w;
    t2 = t1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = w;
}
""")

# 420DE0 nested with no-chain but primed with a nonzero dummy
run("d_420p", 0x00420DE0, 48, """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a, v;

    v = 0x370;
    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v & 4;
}
""")

import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()

S_2740 = """typedef signed char s8;
typedef unsigned char u8;
typedef unsigned int u32;
void func_004B2740(void)
{
    u32 a, v;

    v = 0x402;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 4) = v;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    v = *(volatile s8 *)(a + 0x2c9);
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 0xb) = v;
}
"""

S_0EE0 = """typedef signed char s8;
typedef signed short s16;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
void func_004B0EE0(void)
{
    u32 a;
    s8 b;
    s16 w;

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
"""

for tag, va, sz, src in [("u_2740", 0x004B2740, 48, S_2740), ("u_0EE0", 0x004B0EE0, 80, S_0EE0)]:
    open(f"/home/user/sfzfg/roundtrip/pilots/{tag}.c", "w").write(src)
    o = f"/tmp/{tag}.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"/home/user/sfzfg/roundtrip/pilots/{tag}.c"],
                   capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{tag}: COMPILE FAIL")
        continue
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin", "rb").read()
    tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]
    if got == tgt:
        print(f"*** {tag}: FULL MATCH ***")
    elif len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
        print(f"*** {tag}: MATCH + {len(tgt)-len(got)}B pad ***")
    else:
        print(f"--- {tag}: no (got {len(got)}B vs {sz}B)")
        shown = 0
        for i in range(0, min(len(got), len(tgt)), 4):
            g, t = got[i:i+4].hex(), tgt[i:i+4].hex()
            if g != t:
                print(f"    word {i//4}: got {g} want {t}")
                shown += 1
                if shown >= 6:
                    break

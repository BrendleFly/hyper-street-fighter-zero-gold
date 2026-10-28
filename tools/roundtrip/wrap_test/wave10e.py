import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()

S_420 = """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a, v;
    v = 0;
    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v & 4;
}
"""

def run(tag, va, sz, src):
    open(f"/home/user/sfzfg/roundtrip/pilots/{tag}.c", "w").write(src)
    o = f"/tmp/{tag}.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"/home/user/sfzfg/roundtrip/pilots/{tag}.c"],
                   capture_output=True, text=True)
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
        print(f"--- {tag}: no (got {len(got)}B vs {sz}B, w0={got[:4].hex()})")

run("p_420", 0x00420DE0, 48, S_420)

S_C50 = """typedef signed char s8;
typedef signed int s32;
typedef unsigned int u32;
void func_00301C50(void)
{
    u32 a, v;
    v = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x40);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0xb);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v;
    if (*(volatile u32 *)(a + 0x1150) == 0) {
        a = 0x70000000;
        *(volatile u32 *)(a + 0x1124) = -(s32)*(volatile u32 *)(a + 0x1124);
    }
    a = 0x70000000;
    *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x10) += *(volatile u32 *)(a + 0x1124);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x48);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x40);
    a = 0x70000000;
    *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x40) += *(volatile u32 *)(a + 0x1124);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x40);
    if (*(volatile u32 *)(a + 0x1150) < *(volatile u32 *)(a + 0x1158)) {
        a = 0x70000000;
        *(volatile u32 *)(a + 0x1158) = -1;
    } else {
        a = 0x70000000;
        *(volatile u32 *)(a + 0x1158) = 0;
    }
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = *(volatile u32 *)(a + 0x1150);
}
"""
run("p_c50", 0x00301C50, 288, S_C50)

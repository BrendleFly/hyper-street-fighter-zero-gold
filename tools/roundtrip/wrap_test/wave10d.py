import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()

SRC = """typedef signed char s8;
typedef signed int s32;
typedef unsigned int u32;

void func_00301C50(void)
{
    u32 a;
    s8 v;

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

open("/home/user/sfzfg/roundtrip/pilots/w10_c50.c", "w").write(SRC)
o = "/tmp/w10_c50.o"
if os.path.exists(o):
    os.remove(o)
subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, "/home/user/sfzfg/roundtrip/pilots/w10_c50.c"],
               capture_output=True, text=True)
if not os.path.exists(o):
    print("COMPILE FAIL")
    raise SystemExit
subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
got = open("/tmp/g.bin", "rb").read()
va, sz = 0x00301C50, 288
tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]
if got == tgt:
    print("*** FULL MATCH ***")
elif len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
    print(f"*** MATCH + {len(tgt)-len(got)}B pad ***")
else:
    print(f"mismatch: got {len(got)}B vs {sz}B; first diffs:")
    shown = 0
    for i in range(0, min(len(got), len(tgt)), 4):
        g, t = got[i:i+4].hex(), tgt[i:i+4].hex()
        if g != t:
            print(f"  word {i//4} (@{va+i:#x}): got {g} want {t}")
            shown += 1
            if shown >= 10:
                break

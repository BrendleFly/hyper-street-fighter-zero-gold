import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]

CASES = {
    # T1: x34 group (48B) — unused param hypothesis for li a0,1
    "t1": ("""typedef unsigned int u32;
void t1(u32 param)
{
    u32 a;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = 1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = 1;
}
""", "grp34_target.bin"),
    # T2: x7 group (32B) — li a0,4 then sb a0,4(v1)
    "t2": ("""typedef unsigned int u32;
typedef unsigned char u8;
void t2(u32 param)
{
    volatile u32 *p;
    p = (volatile u32 *)0x70001118;
    *(volatile u8 *)(p[0] + 4) = 4;
}
""", "grp7_target.bin"),
    # T3: x36 group (32B) — += 2 counter
    "t3a": ("""typedef unsigned int u32;
typedef unsigned char u8;
void t3a(void)
{
    volatile u8 *p;
    p = (volatile u8 *)(*(volatile u32 *)0x70001118);
    *p += 2;
}
""", "grp36_target.bin"),
    "t3b": ("""typedef unsigned int u32;
typedef unsigned char u8;
void t3b(void)
{
    u8 *p;
    p = (u8 *)*(volatile u32 *)0x70001118;
    *p = *p + 2;
}
""", "grp36_target.bin"),
    # T4: x23 group (32B) — sb zero,0x3c(v1) after lw v1
    "t4a": ("""typedef unsigned int u32;
typedef unsigned char u8;
void t4a(void)
{
    u8 *p;
    p = (u8 *)*(volatile u32 *)0x70001118;
    p[0x3c] = 0;
}
""", "grp23_target.bin"),
}

img = open("../ro9_original.bin", "rb").read()
GROUP_VA = {"grp34_target.bin": 0x235A00, "grp7_target.bin": 0x51AC80,
            "grp36_target.bin": 0x255590, "grp23_target.bin": 0x2556D0}
os.makedirs("ft", exist_ok=True)
for name, (src, tgt_name) in CASES.items():
    open(f"ft/{name}.c", "w").write(src)
    va = GROUP_VA[tgt_name]
    tgt = img[va - 0x1F0000: va - 0x1F0000 + len(tgt_name) * 0 + (48 if va == 0x235A00 else 32)]
    open(f"ft/{tgt_name}", "wb").write(tgt)
    o = f"/tmp/{name}.o"
    r = subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"ft/{name}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{name}: COMPILE FAIL {r.stderr[:150]}")
        continue
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin", "rb").read()
    if got == tgt:
        print(f"*** {name}: MATCH ***")
    else:
        print(f"--- {name}: size {len(got)} vs {len(tgt)}")
        for i in range(0, min(len(got), len(tgt)), 4):
            g = got[i:i+4].hex()
            t = tgt[i:i+4].hex()
            print(f"  {i:2d}: {g}  {t}  {'OK' if g == t else '<<'}")

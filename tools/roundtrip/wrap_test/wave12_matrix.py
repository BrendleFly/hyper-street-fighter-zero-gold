import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
va, sz = 0x00420DE0, 48
tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]

SHAPES = {}

SHAPES["struct_ptr"] = """typedef signed char s8;
typedef unsigned int u32;
typedef struct {
    u32 pad[0x444];
    u32 ptr;      /* 0x1110 */
    u32 p1114;    /* 0x1114 */
    u32 p1118;    /* 0x1118 */
    u32 x11c[10];
    u32 r1124;    /* 0x1124 */
    u32 x128[10];
    u32 r1150;    /* 0x1150 */
    u32 x154[1];
    u32 r1158;    /* 0x1158 */
} WORK;
void func_00420DE0(void)
{
    volatile WORK *w;
    s8 v;

    w = (volatile WORK *)0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)&w->p1118 + 0x370);
    w->r1150 = v & 4;
}
"""

SHAPES["struct_direct"] = """typedef signed char s8;
typedef unsigned int u32;
typedef struct {
    u32 m[0x444];
    u32 ptr;
    u32 p1114;
    u32 p1118;
} WORK2;
void func_00420DE0(void)
{
    s8 v;
    v = *(volatile s8 *)(*(volatile u32 *)0x70001118 + 0x370);
    *(volatile u32 *)0x70001150 = v & 4;
}
"""

SHAPES["ptr_typed"] = """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    volatile u32 *p;
    s8 v;
    p = (volatile u32 *)0x70001118;
    v = *(volatile s8 *)((volatile u8 *)p + 0x370);
    *(volatile u32 *)0x70001150 = v & 4;
}
"""

SHAPES["two_base"] = """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a, b;
    s8 v;
    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    b = 0x70000000;
    *(volatile u32 *)(b + 0x1150) = v & 4;
}
"""

SHAPES["add_before"] = """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a;
    s8 v;
    a = 0x70000000;
    a += 0x1118;
    v = *(volatile s8 *)(*(volatile u32 *)a + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v & 4;
}
"""

SHAPES["s16_v"] = """typedef signed char s8;
typedef signed short s16;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a;
    s16 v;
    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v & 4;
}
"""

SHAPES["int_v_cast"] = """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 a;
    int v;
    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v & 4;
}
"""

SHAPES["store_first_var"] = """typedef signed char s8;
typedef unsigned int u32;
void func_00420DE0(void)
{
    u32 r, a;
    s8 v;
    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    r = v & 4;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r;
}
"""

results = []
for tag, src in SHAPES.items():
    open(f"/tmp/m12_{tag}.c", "w").write(src)
    for opt in (["-O1"], ["-O2"]):
        o = f"/tmp/m12_{tag}.o"
        if os.path.exists(o):
            os.remove(o)
        subprocess.run([WIBO, MW, "-gccinc"] + opt + ["-c", "-lang", "c", "-str", "readonly",
                       "-sdatathreshold", "0", "-o", o, f"/tmp/m12_{tag}.c"],
                       capture_output=True, text=True)
        if not os.path.exists(o):
            print(f"{tag} {opt}: compile fail")
            continue
        subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
        got = open("/tmp/g.bin", "rb").read()
        if got == tgt:
            print(f"*** MATCH {tag} {opt} exact ***")
            results.append((tag, opt))
        elif len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
            print(f"*** MATCH {tag} {opt} +{len(tgt)-len(got)}B pad ***")
            results.append((tag, opt))
        else:
            w0 = got[:4].hex() if got else "----"
            print(f"    {tag} {opt}: no (got {len(got)}B, w0={w0})")
print("wins:", results)

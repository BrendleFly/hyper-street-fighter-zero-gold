import subprocess, os
MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
va, sz = 0x004B2740, 48
tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]
HDR = "typedef signed char s8;\ntypedef unsigned char u8;\ntypedef unsigned int u32;\n"

shapes = {
"three_vars": HDR + """void func_004B2740(void)
{
    u32 a, v, w;
    v = 0x402;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 4) = v;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    w = *(volatile s8 *)(a + 0x2c9);
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 0xb) = w;
}
""",
"chain_then_var": HDR + """void func_004B2740(void)
{
    u32 a, v;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    v = 0x402;
    *(volatile u32 *)(a + 4) = v;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    v = *(volatile s8 *)(a + 0x2c9);
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 0xb) = v;
}
""",
"no_reassign": HDR + """void func_004B2740(void)
{
    u32 a, v;
    v = 0x402;
    a = 0x70000000;
    *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 4) = v;
    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x2c9);
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0xb) = v;
}
""",
}
for tag, s in shapes.items():
    open("/tmp/wg.c", "w").write(s)
    o = "/tmp/wg.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, "/tmp/wg.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{tag}: COMPILE FAIL")
        continue
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin", "rb").read()
    if got == tgt:
        print(f"*** {tag}: FULL MATCH ***")
    elif len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
        print(f"*** {tag}: MATCH + {len(tgt)-len(got)}B pad ***")
    else:
        w0 = got[:4].hex() if got else "----"
        same = sum(1 for i in range(0, min(len(got), len(tgt)), 4) if got[i:i+4] == tgt[i:i+4])
        print(f"    {tag}: no (w0={w0}, matching words {same}/{len(tgt)//4})")

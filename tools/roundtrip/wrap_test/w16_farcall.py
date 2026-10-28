img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
va = 0x004DBA70
tgt = img[va-0x1F0000:va-0x1F0000+48]
for optset, label in [
    (["-gccinc", "-O0,p", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "128", "-farcall", "off"], "farcall off"),
    (["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "128", "-farcall", "off"], "farcall off -O1"),
    (["-gccinc", "-O0,p", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "128", "-farcall", "on"], "farcall on"),
]:
    open("/tmp/fr.c", "w").write("""typedef unsigned int u32;
extern void func_004DBAD0(void);
extern void func_004DB930(void);
void func_004DBA70(void)
{
    func_004DBAD0();
    func_004DB930();
}
""")
    import subprocess
    subprocess.run(["/home/user/sfzfg/tools/wibo", "/home/user/sfzfg/compilers/mwcps2-3.0b38/mwccps2.exe"] + optset + ["-o", "/tmp/fr.o", "/tmp/fr.c"], capture_output=True, text=True)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", "/tmp/fr.o", "/tmp/fr.bin"], check=False)
    got = open("/tmp/fr.bin", "rb").read()
    match = got == tgt
    print(f"{label}: got={len(got)}B match={match}")
    if not match:
        for i in range(0, min(len(got), len(tgt)), 4):
            g, t = got[i:i+4].hex(), tgt[i:i+4].hex()
            if g != t:
                print(f"    {va+i:08x}: got={g} want={t}")

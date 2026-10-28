img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
va = 0x004DBA70
tgt = img[va-0x1F0000:va-0x1F0000+48]
tests = {
"same_tu": """void func_004DBAD0(void) {}
void func_004DB930(void) {}
void func_004DBA70(void)
{
    func_004DBAD0();
    func_004DB930();
}
""",
"static_inline": """static inline void func_004DBAD0(void) {}
static inline void func_004DB930(void) {}
void func_004DBA70(void)
{
    func_004DBAD0();
    func_004DB930();
}
""",
"decl_no_extern": """void func_004DBAD0(void);
void func_004DB930(void);
void func_004DBA70(void)
{
    func_004DBAD0();
    func_004DB930();
}
""",
}
for tag, src in tests.items():
    open("/tmp/fr.c", "w").write(src)
    import subprocess
    subprocess.run(["/home/user/sfzfg/tools/wibo", "/home/user/sfzfg/compilers/mwcps2-3.0b38/mwccps2.exe", "-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "128", "-o", "/tmp/fr.o", "/tmp/fr.c"], capture_output=True, text=True)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", "/tmp/fr.o", "/tmp/fr.bin"], check=False)
    got = open("/tmp/fr.bin", "rb").read()
    print(f"{tag}: got={len(got)}B match={got==tgt}")
    if not match and len(got) >= 12:
        print(f"    w0={got[:4].hex()} w2={got[8:12].hex()} w3={got[12:16].hex()}")
PYEOF
scp -i ~/.ssh/id_ed25519 -o BatchMode=yes "C:\Users\user\Documents\ZCode\PS2_Decomp\SFZFG Decomp Project/tools/roundtrip/wrap_test/w16_sametu.py" user@build-host.invalid:/home/user/sfzfg/roundtrip/pilots/ && ssh -i ~/.ssh/id_ed25519 -o BatchMode=yes user@build-host.invalid 'cd /home/user/sfzfg/roundtrip && python3 pilots/w16_sametu.py'
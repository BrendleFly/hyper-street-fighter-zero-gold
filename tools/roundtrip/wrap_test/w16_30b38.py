import subprocess, os, glob, hashlib
MW3 = "/home/user/sfzfg/compilers/mwcps2-3.0b38/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
ROOT = "/home/user/sfzfg/roundtrip"
SRC = f"{ROOT}/src_ro9"
BUILD = f"{ROOT}/build_eabi"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
matched = [l.strip().split(":")[0] for l in open(f"{SRC}/matched.txt") if l.strip()]
ok = fail = 0
for stem in matched:
    va = int(stem[5:], 16)
    sz = None
    # find size from matched.txt or s file
    sp = f"{ROOT}/ro9/{stem}.s"
    n = sum(1 for l in open(sp) if l.strip().startswith(".word"))
    sz = n*4
    o = f"/tmp/w3_{stem}.o"
    if os.path.exists(o): os.remove(o)
    r = subprocess.run([WIBO, MW3, "-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0", "-o", o, f"{SRC}/{stem}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{stem}: compile fail"); fail += 1; continue
    subprocess.run(["mipsel-linux-gnu-objcopy", "--set-section-alignment", ".text=4", o, o+".t"], check=True)
    os.replace(o+".t", o)
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin","rb").read()
    tgt = img[va-0x1F0000:va-0x1F0000+sz]
    if got == tgt:
        ok += 1
    else:
        fail += 1
        if fail <= 8:
            print(f"{stem}: NO (got {len(got)}B vs {sz}B, w0={got[:4].hex() if got else '--'})")
print(f"3.0b38 -O1: matched={ok}, failed={fail}, total={len(matched)}")

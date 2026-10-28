import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]

tests = [("w1", "wrap98_target.bin"), ("w2", "wrap98_target.bin"), ("w3", "wrap98_target.bin"),
         ("w4", "grp34_target.bin")]
for src, tgt_name in tests:
    o = f"/tmp/{src}.o"
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, f"{src}.c"], capture_output=True, text=True)
    if not os.path.exists(o):
        print(f"{src}: COMPILE FAILED")
        continue
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text", o, "/tmp/g.bin"], check=False)
    got = open("/tmp/g.bin", "rb").read()
    tgt = open(tgt_name, "rb").read()
    if got == tgt:
        print(f"*** {src}: MATCH ***")
    else:
        print(f"--- {src}: size {len(got)} vs {len(tgt)}")
        for i in range(0, max(len(got), len(tgt)), 4):
            g = got[i:i+4].hex() if i < len(got) else "--------"
            t = tgt[i:i+4].hex() if i < len(tgt) else "--------"
            mark = " " if g == t else "*"
            print(f"  {i:2d}: got {g}  want {t} {mark}")
            if i > 40:
                break

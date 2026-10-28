import subprocess, os

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
FLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]

TWINS = ["004C5230", "004CC180", "002A8C80", "00399AB0", "00489850",
         "002CA3D0", "003BF0D0", "002ECA10", "0027B5D0"]

os.chdir("/home/user/sfzfg/roundtrip/pilots")
for t in TWINS:
    src = open("pilot_e.c").read().replace("func_004C5230", f"func_{t}")
    open(f"func_{t}.c", "w").write(src)
    o = f"/home/user/sfzfg/roundtrip/build_eabi/func_{t}.o"
    r = subprocess.run([WIBO, MW] + FLAGS + ["-o", o, f"func_{t}.c"], capture_output=True, text=True)
    subprocess.run(["mipsel-linux-gnu-objcopy", "--set-section-alignment", ".text=4", o, o + ".t"], check=True)
    os.replace(o + ".t", o)
    print(f"compiled + installed func_{t}.o")

# verify each object's .text equals the target bytes
img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
ok = True
for t in TWINS:
    va = int(t, 16)
    tgt = img[va - 0x1F0000: va - 0x1F0000 + 32]
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text",
                    f"/home/user/sfzfg/roundtrip/build_eabi/func_{t}.o", "/tmp/chk.bin"], check=False)
    got = open("/tmp/chk.bin", "rb").read()
    same = got == tgt
    ok &= same
    print(f"func_{t}: {'BYTE-EXACT' if same else 'MISMATCH ' + got.hex()}")
print("ALL OBJECTS EXACT:", ok)

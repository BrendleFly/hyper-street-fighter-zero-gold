import subprocess, os, itertools

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"

targets = {
    "pilot_a": open("pilot_a_target.bin", "rb").read(),
    "pilot_b": open("pilot_b_target.bin", "rb").read(),
    "pilot_c": open("pilot_b_target.bin", "rb").read(),
}
opts = ["-O0", "-O1", "-O2", "-O3", "-O4", "-O4,p", "-O0,p", "-O1,p", "-O2,p", "-O3,p"]
procs = ["", "-proc r5900", "-proc 5900"]
results = []
for src in ("pilot_a", "pilot_b", "pilot_c"):
    for opt, proc in itertools.product(opts, procs):
        tag = f"{src} {opt} {proc}".strip().replace(" ", "_")
        o = f"/tmp/m_{tag}.o"
        cmd = [WIBO, MW, "-gccinc", opt, "-c", "-lang", "c", "-str", "readonly",
               "-sdatathreshold", "0"] + ([proc] if proc else []) + ["-o", o, f"{src}.c"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if not os.path.exists(o):
            continue
        subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text",
                        o, "/tmp/m.bin"], check=False)
        got = open("/tmp/m.bin", "rb").read()
        tgt = targets[src]
        if got == tgt:
            print(f"*** MATCH: {src} [{opt} {proc}]")
            results.append((src, opt, proc))
        elif len(got) == len(tgt):
            for i in range(0, len(got), 4):
                if got[i:i + 4] != tgt[i:i + 4]:
                    print(f"    {src} [{opt} {proc}]: same-size, first diff word {i//4}: "
                          f"got {got[i:i+4].hex()} want {tgt[i:i+4].hex()}")
                    break
print()
print("MATCHES:", results)

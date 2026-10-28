#!/usr/bin/env python3
"""Formulation permuter for SFZFG ro9 matching.

Enumerates C formulations for a small scratchpad function and byte-tests each
against the original. Run ON build-box:  python3 permuter.py <VA> <size> [group_mode]
Writes winning formulation to stdout and src_ro9/ on match.
"""
import subprocess, os, sys, itertools

MW = "/home/user/sfzfg/compilers/mwcps2-2.4-001213/mwccps2.exe"
WIBO = "/home/user/sfzfg/tools/wibo"
CFLAGS = ["-gccinc", "-O1", "-c", "-lang", "c", "-str", "readonly", "-sdatathreshold", "0"]
ROOT = "/home/user/sfzfg/roundtrip"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()


def test_src(src, name):
    fn = f"/tmp/perm_{name}.c"
    open(fn, "w").write(src)
    o = f"/tmp/perm_{name}.o"
    if os.path.exists(o):
        os.remove(o)
    subprocess.run([WIBO, MW] + CFLAGS + ["-o", o, fn], capture_output=True, text=True)
    if not os.path.exists(o):
        return None
    subprocess.run(["mipsel-linux-gnu-objcopy", "-O", "binary", "--only-section=.text",
                    o, "/tmp/perm.bin"], check=False)
    return open("/tmp/perm.bin", "rb").read()


def shapes_420(va):
    """Shape space for the lb flag-test family."""
    name = f"{va:08X}"
    out = []
    for vfirst in (False, True):
        for chain in (False, True):
            decl = "    s8 v;\n    u32 a;\n" if vfirst else "    u32 a;\n    s8 v;\n"
            if chain:
                body = ("    a = 0x70000000;\n"
                        "    a = *(volatile u32 *)(a + 0x1118);\n"
                        "    v = *(volatile s8 *)(a + 0x370);\n"
                        "    a = 0x70000000;\n"
                        "    *(volatile u32 *)(a + 0x1150) = v & 4;\n")
            else:
                body = ("    a = 0x70000000;\n"
                        "    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);\n"
                        "    a = 0x70000000;\n"
                        "    *(volatile u32 *)(a + 0x1150) = v & 4;\n")
            out.append(("chain" if chain else "direct", f"""typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
{decl}{body}}}
"""))
    # single-var chained variant
    out.append(("single", f"""typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 a;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    a = *(volatile s8 *)(a + 0x370);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = (a & 4);
}}
"""))
    # andi result via separate first-declared var
    out.append(("res_first", f"""typedef signed char s8;
typedef unsigned int u32;
void func_{name}(void)
{{
    u32 r;
    u32 a;
    s8 v;

    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    r = v & 4;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = r;
}}
"""))
    return out


def main():
    va = int(sys.argv[1], 16)
    sz = int(sys.argv[2], 16 if sys.argv[2].startswith("0x") else 10)
    tgt = img[va - 0x1F0000: va - 0x1F0000 + sz]
    tried = 0
    for tag, src in shapes_420(va):
        tried += 1
        got = test_src(src, f"{va:08X}_{tried}")
        if got is None:
            continue
        if got == tgt:
            print(f"MATCH [{tag}] exact")
            open(f"{ROOT}/src_ro9/func_{va:08X}.c", "w").write(src)
            return
        if len(got) < len(tgt) and tgt[:len(got)] == got and set(tgt[len(got):]) <= {0}:
            pad = len(tgt) - len(got)
            print(f"MATCH [{tag}] + {pad}B pad")
            open(f"{ROOT}/src_ro9/func_{va:08X}.c", "w").write(src)
            open(f"{ROOT}/src_ro9/matched.txt", "a").write(f"func_{va:08X}:{pad}\n")
            return
    print(f"no match in {tried} shapes")


if __name__ == "__main__":
    main()

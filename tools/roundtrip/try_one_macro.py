#!/usr/bin/env python3
"""Run gen_macro2's build path on ONE function, then verify with install_wins2.

Usage: python3 try_one_macro.py 002248D0

Prints the STOP reason per base config and, for any build, the install result.
Keeps the generated C in /tmp/one_<base>_<data>.c for inspection.
"""
import subprocess
import sys

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import gen_c_family4 as G          # noqa: E402
import gen_macro2 as M             # noqa: E402


def main():
    arg = sys.argv[1].strip()
    stem = arg if arg.startswith("func_") else "func_" + arg.upper()
    va, size, insns = G.load_insns(stem)
    print(f"loaded {stem}: size={size} bytes, {len(insns)} insns")

    stripped = G.strip_call_frame(insns)
    if stripped is None:
        print("REJECT: frame (strip_call_frame returned None)")
        return
    print(f"stripped frame: {len(stripped)} insns")
    if not any(i.mnemonic == "jal" for i in stripped):
        print("REJECT: no-call")
        return

    # mirror gen_macro2.main()'s monkey-patching
    G.decode_run = M.macro_decode_run
    G.extract_cond = M.macro_extract_cond

    cfgs = (("$3", "$3", None), ("$2", "$2", None),
            ("$2", "$3", None), ("$2", "$2", "$3"))
    for base, data, widen in cfgs:
        tag = f"{base}/{data}/{widen or 'auto'}"
        try:
            M.CTX = M.Ctx(base)
            segs, alias = M.structure_local(stripped, va, size)
            src = M.build_macro_source(va, M.macros_for(base, data, widen), segs, M.CTX)
        except G.Stop as e:
            print(f"{tag}: STOP {e}")
            continue
        except Exception as e:                     # noqa: BLE001
            print(f"{tag}: EXC {type(e).__name__}: {e}")
            continue
        path = "/tmp/one_%s_%s_%s.c" % (base.replace("$", ""), data.replace("$", ""),
                                        (widen or "auto").replace("$", ""))
        open(path, "w").write(src)
        print(f"{base}/{data}: BUILT ({len(src)} chars) -> {path}")

        spec_path = "/tmp/one_spec_%s_%s_%s.txt" % (
            base.replace("$", ""), data.replace("$", ""),
            (widen or "auto").replace("$", ""))
        open(spec_path, "w").write(
            f"VA {va:08X}\nSIZE {size:X}\nCOMP ee-gcc2.96\nEND\n{src}---\n")
        r = subprocess.run(
            ["python3", f"{G.ROOT}/pilots/install_wins2.py", spec_path],
            capture_output=True, text=True)
        out = r.stdout.strip()
        print("  install:", out.splitlines()[-1] if out else "(no output)")
        if "MATCH" in out:
            print("  *** MATCH ***")
        if r.stderr.strip():
            print("  stderr:", r.stderr.strip()[-300:])


if __name__ == "__main__":
    main()

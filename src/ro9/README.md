# ro9 (Hyper Street Fighter Alpha) decompilation sources

- `matched.txt` — stems of functions decompiled to C (one per line).
- `func_XXXXXXXX.c` — one C file per matched function.
- `common.h` — shared types.
- `match_build.py` — build-box-side build driver (sync this dir to
  build-box:~/sfzfg/roundtrip/src_ro9/, then `python3 match_build.py`):
  compiles matched C with mwccps2 2.4.1.01 (flags: -gccinc -O1 -lang c
  -str readonly -sdatathreshold 0), assembles the remaining .s with
  mipsel-linux-gnu-as (-EL -march=r5900 -mabi=eabi -G 128), links via
  roundtrip_eabi.ld, byte-compares vs ro9_original.bin. Must always print
  FULL IMAGE BYTE-EXACT.

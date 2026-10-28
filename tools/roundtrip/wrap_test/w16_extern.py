img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
va = 0x004DBA70
tgt = img[va-0x1F0000:va-0x1F0000+48]
got = open("/tmp/fr30b.bin", "rb").read()
print("got:", got.hex(" "))
print("want:", tgt.hex(" "))
for i in range(0, min(len(got), len(tgt)), 4):
    g, t = got[i:i+4].hex(), tgt[i:i+4].hex()
    print(f"  {va+i:08x}: got={g} want={t}" + ("" if g == t else "  <<"))

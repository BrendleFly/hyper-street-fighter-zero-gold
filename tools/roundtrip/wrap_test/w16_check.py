img = open("/home/user/sfzfg/roundtrip/ro9_original.bin", "rb").read()
rt = open("/home/user/sfzfg/roundtrip/ro9_rt.bin", "rb").read()
va = 0x004DBA70
print("orig:", img[va-0x1F0000:va-0x1F0000+48].hex(" "))
print("got :", rt[va-0x1F0000:va-0x1F0000+48].hex(" "))
for i in range(0, 48, 4):
    o = va - 0x1F0000 + i
    print(f"  {va+i:08x}: orig={img[o:o+4].hex()} got={rt[o:o+4].hex()}")

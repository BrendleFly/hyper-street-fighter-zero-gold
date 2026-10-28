typedef unsigned char u8;
typedef unsigned int u32;

void func_002DEF00(void)
{
    u32 a, v;

    v = 8;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1110);
    *(volatile u8 *)(a + 0xcc) = v;
    v = 2;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1110);
    *(volatile u8 *)(a + 0xee) = v;
    v = 8;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1110);
    *(volatile u8 *)(a + 0xef) = v;
}

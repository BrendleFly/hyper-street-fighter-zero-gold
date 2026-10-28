typedef unsigned char u8;
typedef unsigned int u32;

void func_00559B90(void)
{
    u32 a, v;

    v = 4;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 4) = v;
}

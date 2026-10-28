typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_004B2740(void)
{
    u32 a;
    u32 w;
    s8 v;

    w = 0x402;
    a = 0x70000000;
    *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x4) = w;
    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x2c9);
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0xb) = v;
}

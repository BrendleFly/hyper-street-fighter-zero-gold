typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_002E6620(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    v1 = 0x402;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 0x4) = v1;
    v2 = 0x4;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 0x80) = v2;
}

typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_00369890(void)
{
    u32 a, v;
    volatile s8 v;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 0x1124) = 0;
    v = *(volatile s8 *)(a + 0x1124);
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 0x2c8) = v;
    v = *(volatile s8 *)(a + 0x1124);
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 0x5b) = v;
}

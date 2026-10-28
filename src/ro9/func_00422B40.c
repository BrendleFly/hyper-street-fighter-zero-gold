typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_00422B40(void)
{
    u32 a;
    s8 v;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = 0;
    a = 0x70000000;
    v = *(volatile s8 *)(a + 0x1124);
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0x2c8) = v;
    a = 0x70000000;
    v = *(volatile s8 *)(a + 0x1124);
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0x5b) = v;
}

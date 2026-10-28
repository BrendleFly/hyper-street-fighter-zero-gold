typedef signed char s8;
typedef signed short s16;
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

void func_0036A910(void)
{
    u32 a;
    s8 b;
    s16 w;

    a = 0x70000000;
    b = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x379);
    *(volatile u8 *)(a + 0x1124) = b;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    w = *(volatile s16 *)(a + 0x1124);
    w &= 0x77;
    *(volatile u16 *)(a + 0x1124) = w;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = w;
}

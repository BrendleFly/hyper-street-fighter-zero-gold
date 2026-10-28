typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_00334910(void)
{
    u32 a;
    u32 w;

    a = 0x70000000;
    *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x84) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    w = 1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = w;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = w;
}

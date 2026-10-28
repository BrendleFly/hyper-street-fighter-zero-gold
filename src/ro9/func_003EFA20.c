typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_003EFA20(void)
{
    u32 a;
    u32 w;

    w = 8;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 7) = w;
    w = 0xfffc0000;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 0x40) = w;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 0x44) = 0;
    w = 0x2000;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 0x48) = w;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 0x4c) = 0;
}

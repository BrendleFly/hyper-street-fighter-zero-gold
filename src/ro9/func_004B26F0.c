typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_004B26F0(void)
{
    u32 a;
    s8 v;
    u32 w;

    a = 0x70000000;
    v = *(volatile s8 *)(a + 0x1128);
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0x81) = v;
    a = 0x70000000;
    v = *(volatile s8 *)(a + 0x112c);
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0x80) = v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    w = 1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = w;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = w;
}

typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_0027D890(void)
{
    u32 a;
    u32 v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    v = 0x1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1144) = v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v;
}

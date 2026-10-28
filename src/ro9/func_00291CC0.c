typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_00291CC0(void)
{
    u32 a;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1114);
    *(volatile u8 *)(a + 0x137) = 0;
}

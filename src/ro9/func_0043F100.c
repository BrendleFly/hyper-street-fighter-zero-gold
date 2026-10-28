typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_0043F100(void)
{
    u32 a;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u16 *)(a + 0x276) = 0;
}

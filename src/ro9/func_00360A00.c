typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_00360A00(void)
{
    u32 a;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = 0;
}

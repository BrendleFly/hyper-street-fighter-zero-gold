typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_00305A10(void)
{
    u32 a;
    u32 v;
    v = 0x1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = v;
}

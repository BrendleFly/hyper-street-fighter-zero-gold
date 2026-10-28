typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_00237F00(void)
{
    u32 a;
    u32 w;

    w = 0x0a0c0002;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1104);
    *(volatile u32 *)(a + 4) = w;
}

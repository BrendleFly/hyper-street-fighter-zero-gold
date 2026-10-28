typedef signed char s8;
typedef unsigned int u32;

void func_00420F00(void)
{
    u32 a;
    s8 *p;

    a = 0x70000000;
    p = (s8 *)(*(volatile u32 *)(a + 0x1118));
    *(volatile s8 *)(p + 0xb) ^= 1;
}

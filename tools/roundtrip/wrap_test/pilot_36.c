typedef signed char s8;
typedef unsigned int u32;

void func_00255590(void)
{
    u32 a;
    volatile s8 *p;

    a = 0x70000000;
    p = (volatile s8 *)(*(volatile u32 *)(a + 0x1118));
    p[4] += 2;
}

asm void pad_00255590(void)
{
    nop
}

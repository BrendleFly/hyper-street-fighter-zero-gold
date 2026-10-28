typedef unsigned int u32;
typedef signed char s8;

void func_00257660(void)
{
    u32 a;
    volatile s8 *p;

    a = 0x70000000;
    p = (volatile s8 *)(*(volatile u32 *)(a + 0x1118));
    p[4] += 2;
}

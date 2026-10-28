typedef signed char s8;
typedef unsigned int u32;

void func_0028EF40(void)
{
    u32 a;
    s8 v;
    s8 *p;

    a = 0x70000000;
    p = (s8 *)(*(volatile u32 *)(a + 0x1118));
    v = *(volatile s8 *)(p + 0xb4);
    *(volatile s8 *)(p + 0xb4) = v | -0x80;
}

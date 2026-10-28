typedef signed char s8;
typedef unsigned int u32;

void func_00420DE0(void)
{
    u32 a;
    s8 v;

    a = 0x70000000;
    v = *(volatile s8 *)(*(volatile u32 *)(a + 0x1118) + 0x370);
    *(volatile u32 *)(a + 0x1150) = v & 4;
}

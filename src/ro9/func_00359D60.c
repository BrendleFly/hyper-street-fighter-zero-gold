typedef unsigned int u32;

void func_00359D60(void)
{
    u32 a, v;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    v = 1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v;
}

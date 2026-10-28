typedef unsigned int u32;

void func_00325BB0(void)
{
    u32 a;
    u32 v;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 0x84) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    v = 1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = v;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = v;
}

typedef unsigned char u8;
typedef unsigned int u32;

void func_00301DA0(void)
{
    u32 a;
    volatile u32 *q;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x44);
    a = 0x70000000;
    q = (volatile u32 *)(*(volatile u32 *)(a + 0x1118));
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) += *(volatile u32 *)((volatile u8 *)q + 0x14);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) += *(volatile u32 *)((volatile u8 *)q + 0x4c);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x44) = *(volatile u32 *)(a + 0x1124);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = *(volatile u32 *)(a + 0x1124);
}

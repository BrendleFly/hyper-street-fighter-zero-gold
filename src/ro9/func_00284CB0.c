typedef unsigned char u8;
typedef unsigned int u32;

void func_00284CB0(void)
{
    u32 a;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = 0;
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1114) + 0x181) = 0;
}

typedef unsigned char u8;
typedef unsigned int u32;

void func_002584C0(void)
{
    u32 a;

    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 0x3c) = 0;
}

typedef unsigned int u32;

/* pilot E — func_003BF0D0: int temp for the page base */
void func_003BF0D0(void)
{
    u32 a;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = 0;
}

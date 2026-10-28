typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

void func_002790E0(void)
{
    u32 a;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 0x201) = 0;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u16 *)(a + 0x202) = 0;
}

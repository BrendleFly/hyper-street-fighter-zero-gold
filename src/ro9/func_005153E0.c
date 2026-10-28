typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_005153E0(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    u32 v3;
    v1 = 0x1;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1110);
    *(volatile u8 *)(a + 0xc) = v1;
    v2 = 0x1;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x110c);
    *(volatile u8 *)(a + 0xc) = v2;
    v3 = 0x1;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1108);
    *(volatile u8 *)(a + 0xc) = v3;
}

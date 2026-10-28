typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_005153B0(void)
{
    u32 a;
    u32 p;
    s8 v;

    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x110c);
    v = *(volatile s8 *)(p + 0xd);
    *(volatile s8 *)(p + 0xd) = v - 1;
    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x1108);
    v = *(volatile s8 *)(p + 0xd);
    *(volatile s8 *)(p + 0xd) = v - 1;
}

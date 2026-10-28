typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_0051B630(void)
{
    u32 a;
    u32 p;
    s8 v;

    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x1118);
    v = *(volatile s8 *)(p + 4);
    *(volatile s8 *)(p + 4) = v + 2;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 5) = 0;
}

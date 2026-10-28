typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_0030EFE0(void)
{
    u32 a;
    u32 v;
    u32 p;
    u32 s;

    a = 0x70000000;
    v = *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x44);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = v;
    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x1118);
    v = *(volatile u32 *)(p + 0x14);
    a = 0x70000000;
    s = *(volatile u32 *)(a + 0x1124);
    *(volatile u32 *)(p + 0x14) = v + s;
    a = 0x70000000;
    v = *(volatile u32 *)(*(volatile u32 *)(a + 0x1118) + 0x4c);
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = v;
    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x1118);
    v = *(volatile u32 *)(p + 0x44);
    a = 0x70000000;
    s = *(volatile u32 *)(a + 0x1124);
    *(volatile u32 *)(p + 0x44) = v + s;
}

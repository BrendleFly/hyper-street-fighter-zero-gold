typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_002DD870(void)
{
    u32 a;
    u32 p;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1128) = 0;
    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x1118);
    p += 0x188;
    *(volatile u32 *)(p) = 0;
    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x1118);
    p += 0x18c;
    *(volatile u32 *)(p) = 0;
    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x1118);
    p += 0x190;
    *(volatile u32 *)(p) = 0;
    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x1118);
    p += 0x194;
    *(volatile u32 *)(p) = 0;
    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x1118);
    p += 0x1a0;
    *(volatile u32 *)(p) = 0;
    a = 0x70000000;
    p = *(volatile u32 *)(a + 0x1118);
    p += 0x1a4;
    *(volatile u32 *)(p) = 0;
}

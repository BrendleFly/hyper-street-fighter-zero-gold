typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_004B79F0(void)
{
    u32 a, v;
    volatile s16 v;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1114);
    v = *(volatile s16 *)(a + 0x100);
    *(volatile u16 *)(a + 0x1124) = v;
    v = 0x8;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 0xe) = v;
}

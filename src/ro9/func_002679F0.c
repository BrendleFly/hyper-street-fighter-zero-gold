typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_002679F0(void)
{
    u32 a;
    s8 v8;
    s16 v16;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = 0;
    a = 0x70000000;
    v8 = *(volatile s8 *)(a + 0x1124);
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1118) + 1) = v8;
    a = 0x70000000;
    v16 = *(volatile s16 *)(a + 0x1124);
    a = 0x70000000;
    *(volatile u16 *)(*(volatile u32 *)(a + 0x1118) + 0x24) = v16;
}

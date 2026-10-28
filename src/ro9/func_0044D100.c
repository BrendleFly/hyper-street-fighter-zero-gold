typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004A8F10();
void func_0044D100(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    s32 v3;
    u32 v4;
    u32 v5;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    *(volatile s8 *)(v1 + 6) = *(volatile s8 *)(v1 + 6) + 2;
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    v3 = *(volatile s8 *)(v2 + 713);
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v4 + 11) = v3;
    a = 0x70000000;
    v5 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v5 + 132) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 4388) = 0;
    ((void (*)(void))func_004A8F10)();
}

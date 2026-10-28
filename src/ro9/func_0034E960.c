typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_005783A0();
extern void func_004B5E70();
void func_0034E960(void)
{
    u32 a;
    u32 v1;
    s32 v2;
    u32 v3;
    s32 v4;
    u32 v5;
    s32 v6;
    u32 v7;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    v2 = *(volatile s16 *)(v1 + 100);
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v3 + 22) = v2;
    ((void (*)(void))func_005783A0)();
    a = 0x70000000;
    *(volatile u32 *)(a + 4388) = 0;
    a = 0x70000000;
    v4 = *(volatile s8 *)(a + 4388);
    a = 0x70000000;
    v5 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v5 + 49) = v4;
    a = 0x70000000;
    v6 = *(volatile s16 *)(a + 4388);
    a = 0x70000000;
    v7 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v7 + 20) = v6;
    ((void (*)(void))func_004B5E70)();
}

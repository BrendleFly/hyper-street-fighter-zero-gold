typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_005249E0();
void func_00524970(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    s32 v3;
    u32 v4;
    s32 v5;
    u32 v6;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    *(volatile s8 *)(v1 + 5) = *(volatile s8 *)(v1 + 5) + 2;
    a = 0x70000000;
    *(volatile u32 *)(a + 4388) = 0;
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    v3 = *(volatile s16 *)(v2 + 72);
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v4 + 18) = v3;
    a = 0x70000000;
    v5 = *(volatile s16 *)(a + 4388);
    a = 0x70000000;
    v6 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v6 + 16) = v5;
    func_005249E0();
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004AAC20();
extern void func_003B7040();
extern void func_004B5E70();
void func_003B4E30(void)
{
    u32 a;
    s32 v1;
    u32 v2;
    u32 v3;
    s32 v4;
    u32 v5;
    u32 v6;
    u32 v7;
    ((void (*)(void))func_004AAC20)();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4440);
    if (v1 >= 0) {
        func_003B7040();
    } else {
        a = 0x70000000;
        v2 = *(volatile u32 *)(a + 4376);
        *(volatile s8 *)(v2 + 7) = *(volatile s8 *)(v2 + 7) + 2;
        a = 0x70000000;
        v3 = *(volatile u32 *)(a + 4376);
        v4 = *(volatile s16 *)(v3 + 100);
        a = 0x70000000;
        v5 = *(volatile u32 *)(a + 4376);
        *(volatile u16 *)(v5 + 22) = v4;
        a = 0x70000000;
        v6 = *(volatile u32 *)(a + 4376);
        *(volatile u16 *)(v6 + 20) = 0;
        a = 0x70000000;
        v7 = *(volatile u32 *)(a + 4376);
        *(volatile u8 *)(v7 + 49) = 0;
        ((void (*)(void))func_004B5E70)();
    }
}

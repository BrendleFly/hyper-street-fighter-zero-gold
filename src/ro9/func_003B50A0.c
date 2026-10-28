typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004AAC20();
extern void func_003B7040();
extern void func_004B5E70();
void func_003B50A0(void)
{
    u32 a;
    s32 v1;
    u32 v2;
    s32 v3;
    u32 v4;
    s32 v5;
    u32 v6;
    s32 v7;
    u32 v8;
    ((void (*)(void))func_004AAC20)();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4440);
    if (v1 >= 0) {
        func_003B7040();
    } else {
        a = 0x70000000;
        v2 = *(volatile u32 *)(a + 4376);
        v3 = *(volatile s16 *)(v2 + 100);
        a = 0x70000000;
        v4 = *(volatile u32 *)(a + 4376);
        *(volatile u16 *)(v4 + 22) = v3;
        a = 0x70000000;
        *(volatile u32 *)(a + 4388) = 0;
        a = 0x70000000;
        v5 = *(volatile s16 *)(a + 4388);
        a = 0x70000000;
        v6 = *(volatile u32 *)(a + 4376);
        *(volatile u16 *)(v6 + 20) = v5;
        a = 0x70000000;
        v7 = *(volatile s8 *)(a + 4388);
        a = 0x70000000;
        v8 = *(volatile u32 *)(a + 4376);
        *(volatile u8 *)(v8 + 49) = v7;
        ((void (*)(void))func_004B5E70)();
    }
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_0030A7A0();
extern void func_0030EF30();
extern void func_004A96E0();
void func_0030A720(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    s32 v3;
    a = 0x70000000;
    *(volatile u32 *)(a + 4440) = 0;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    v2 = *(volatile u32 *)(v1 + 64);
    a = 0x70000000;
    *(volatile u32 *)(a + 4388) = v2;
    a = 0x70000000;
    *(volatile u32 *)(a + 4432) = v2;
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4432);
    if (v3 < 0) {
        func_0030A7A0();
    } else {
        func_0030EF30();
        ((void (*)(void))func_004A96E0)();
    }
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004AAC20();
extern void func_0043EFF0();
void func_0043BE40(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    s32 v3;
    u32 v4;
    u32 v5;
    u32 v6;
    ((void (*)(void))func_004AAC20)();
    a = 0x70000000;
    *(volatile u32 *)(a + 4440) = 0;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    v2 = *(volatile u32 *)(v1 + 68);
    a = 0x70000000;
    *(volatile u32 *)(a + 4432) = v2;
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4432);
    if (v3 >= 0) {
        func_0043EFF0();
    } else {
        a = 0x70000000;
        v4 = *(volatile u32 *)(a + 4376);
        *(volatile s8 *)(v4 + 7) = *(volatile s8 *)(v4 + 7) + 2;
        a = 0x70000000;
        v5 = *(volatile u32 *)(a + 4376);
        *(volatile u32 *)(v5 + 64) = 0;
        a = 0x70000000;
        v6 = *(volatile u32 *)(a + 4376);
        *(volatile u32 *)(v6 + 72) = 0;
    }
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_003D4ED0();
extern void func_004A96E0();
void func_003D0DE0(void)
{
    u32 a;
    s32 v1;
    s32 v2;
    ((void (*)(void))func_003D4ED0)();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4432);
    if (v1 < 0) {
        a = 0x70000000;
        v2 = *(volatile u32 *)(a + 4376);
        *(volatile s8 *)(v2 + 7) = *(volatile s8 *)(v2 + 7) + 2;
    }
    ((void (*)(void))func_004A96E0)();
}

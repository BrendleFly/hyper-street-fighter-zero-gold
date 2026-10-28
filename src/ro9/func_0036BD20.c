typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004AAC20();
extern void func_0036B090();
extern void func_004B5E70();
void func_0036BD20(void)
{
    u32 a;
    s32 v1;
    u32 v2;
    ((void (*)(void))func_004AAC20)();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4440);
    if (v1 >= 0) {
        func_0036B090();
    } else {
        a = 0x70000000;
        v2 = *(volatile u32 *)(a + 4376);
        *(volatile s8 *)(v2 + 11) = *(volatile s8 *)(v2 + 11) ^ 1;
        ((void (*)(void))func_004B5E70)();
    }
}

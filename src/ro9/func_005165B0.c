typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00578010();
extern void func_005174E0();
extern void func_00516250();
void func_005165B0(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    s32 v3;
    u32 v4;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v1 + 9) = 0;
    ((void (*)(void))func_00578010)();
    func_005174E0();
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    v3 = *(volatile s16 *)(v2 + 18);
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v4 + 66) = v3;
    func_00516250();
}

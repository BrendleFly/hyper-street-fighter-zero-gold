typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00533410();
extern void func_00528B90();
void func_005289E0(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    u32 v3;
    s32 v4;
    u32 v5;
    func_00533410();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4432);
    if (v1) {
        a = 0x70000000;
        v2 = *(volatile u32 *)(a + 4376);
        *(volatile s8 *)(v2 + 6) = *(volatile s8 *)(v2 + 6) + 2;
        a = 0x70000000;
        v3 = *(volatile u32 *)(a + 4376);
        v4 = *(volatile s16 *)(v3 + 72);
        a = 0x70000000;
        v5 = *(volatile u32 *)(a + 4376);
        *(volatile u16 *)(v5 + 18) = v4;
        a = 0x70000000;
        v1 = *(volatile u32 *)(a + 4376);
        *(volatile u16 *)(v1 + 16) = 0;
    }
    func_00528B90();
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00533410();
extern void func_0052E040();
void func_0052D160(void)
{
    u32 a;
    u32 v1;
    s32 v2;
    u32 v3;
    u32 v4;
    u32 v5;
    u32 v6;
    u32 v7;
    u32 v8;
    s32 v9;
    u32 v10;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    v2 = *(volatile s16 *)(v1 + 36);
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v3 + 18) = v2;
    func_00533410();
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4432);
    if (v4) {
        a = 0x70000000;
        v5 = *(volatile u32 *)(a + 4376);
        *(volatile s8 *)(v5 + 6) = *(volatile s8 *)(v5 + 6) + 2;
        a = 0x70000000;
        v6 = *(volatile u32 *)(a + 4376);
        v2 = *(volatile s16 *)(v6 + 72);
        a = 0x70000000;
        v7 = *(volatile u32 *)(a + 4376);
        *(volatile u16 *)(v7 + 18) = v2;
        a = 0x70000000;
        v4 = *(volatile u32 *)(a + 4376);
        *(volatile u16 *)(v4 + 16) = 0;
    }
    a = 0x70000000;
    v8 = *(volatile u32 *)(a + 4376);
    v9 = *(volatile s16 *)(v8 + 18);
    a = 0x70000000;
    v10 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v10 + 36) = v9;
    func_0052E040();
}

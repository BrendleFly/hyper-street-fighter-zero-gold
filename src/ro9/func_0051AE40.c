typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_0051C630();
void func_0051AE40(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    u32 v3;
    u32 v4;
    s32 v5;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    *(volatile s8 *)(v1 + 4) = *(volatile s8 *)(v1 + 4) + 2;
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v2 + 9) = 0;
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v3 + 26) = 0;
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4376);
    v5 = *(volatile s8 *)(v4 + 60);
    a = 0x70000000;
    *(volatile u8 *)(a + 4388) = v5;
    func_0051C630();
}

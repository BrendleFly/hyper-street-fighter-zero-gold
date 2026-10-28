typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_0036AA90();
void func_0036AA30(void)
{
    u32 a;
    s32 v1;
    u32 v2;
    s32 v3;
    u32 v4;
    u32 v5;
    s32 v6;
    u32 v7;
    func_0036AA90();
    a = 0x70000000;
    v1 = *(volatile s8 *)(a + 4392);
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v2 + 130) = v1;
    a = 0x70000000;
    v3 = *(volatile s8 *)(a + 4396);
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v4 + 129) = v3;
    a = 0x70000000;
    v5 = *(volatile u32 *)(a + 4376);
    v6 = *(volatile s8 *)(v5 + 880);
    a = 0x70000000;
    v7 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v7 + 131) = v6;
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
void func_0022F980(void)
{
    u32 a;
    u32 v1;
    s32 v2;
    u32 v3;
    u32 v4;
    u32 v5;
    u32 v6;
    u32 v7;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4372);
    v2 = *(volatile s16 *)(v1 + 52);
    *(volatile u16 *)0xBE2150 = v2;
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4372);
    v4 = *(volatile u32 *)(v3 - 16044);
    *(volatile u32 *)0xBE2114 = v4;
    a = 0x70000000;
    v5 = *(volatile u32 *)(a + 4372);
    v6 = *(volatile u32 *)(v5 - 16064);
    a = 0x70000000;
    v7 = *(volatile u32 *)(a + 4372);
    *(volatile u32 *)(v7 - 16044) = v6;
}

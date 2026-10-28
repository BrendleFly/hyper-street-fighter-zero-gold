typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
void func_00263450(void)
{
    u32 a;
    u32 v1;
    s32 v2;
    u32 v3;
    u32 v4;
    s32 v5;
    u32 v6;
    u32 v7;
    s32 v8;
    u32 v9;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4368);
    v2 = *(volatile s8 *)(v1 + 11);
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v3 + 11) = v2;
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4368);
    v5 = *(volatile s16 *)(v4 + 18);
    a = 0x70000000;
    v6 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v6 + 18) = v5;
    a = 0x70000000;
    v7 = *(volatile u32 *)(a + 4368);
    v8 = *(volatile s16 *)(v7 + 22);
    a = 0x70000000;
    v9 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v9 + 22) = v8;
}

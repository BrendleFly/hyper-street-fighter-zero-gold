typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004B5E70();
void func_003375F0(void)
{
    u32 a;
    s32 v1;
    u32 v2;
    s32 v3;
    u32 v4;
    a = 0x70000000;
    *(volatile u32 *)(a + 4388) = 0;
    a = 0x70000000;
    v1 = *(volatile s8 *)(a + 4388);
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v2 + 169) = v1;
    a = 0x70000000;
    v3 = *(volatile s8 *)(a + 4388);
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v4 + 7) = v3;
    ((void (*)(void))func_004B5E70)();
}

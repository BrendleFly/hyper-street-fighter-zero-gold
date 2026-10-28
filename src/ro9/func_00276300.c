typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00276080();
void func_00276300(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    u32 v3;
    u32 v4;
    s32 v5;
    u32 v6;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v1 + 516) = 0;
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v2 + 533) = 0;
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v3 + 597) = 0;
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4376);
    v5 = *(volatile s16 *)(v4 + 536);
    a = 0x70000000;
    v6 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v6 + 518) = v5;
    func_00276080();
}

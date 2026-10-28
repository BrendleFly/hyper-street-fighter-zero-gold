typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00522900();
void func_005228C0(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    *(volatile s8 *)(v1 + 4) = *(volatile s8 *)(v1 + 4) + 2;
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v2 + 5) = 0;
    func_00522900();
}

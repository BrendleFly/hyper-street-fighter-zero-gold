typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00299BE0();
void func_00299BA0(void)
{
    u32 a;
    u32 v1;
    s32 v2;
    s32 v3;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4372);
    v2 = *(volatile s16 *)(v1 - 24912);
    a = 0x70000000;
    v3 = *(volatile s16 *)(a + 4388);
    *(volatile u16 *)(v1 - 24912) = (v2 + v3);
    func_00299BE0();
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00305A10();
void func_003053D0(void)
{
    u32 a;
    u32 v;
    v = 0x2;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 0x82) = v;
    func_00305A10();
}

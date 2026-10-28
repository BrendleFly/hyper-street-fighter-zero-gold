typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_002830E0();
void func_00282E50(void)
{
    u32 a;
    u32 v;
    v = 0x1c;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1138) = v;
    func_002830E0();
}

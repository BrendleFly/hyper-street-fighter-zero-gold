typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00250D70();
void func_00250D40(void)
{
    u32 a;
    u32 v;
    v = 0x1f;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1140) = v;
    func_00250D70();
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00582D70();
void func_00582D10(void)
{
    u32 a;
    u32 v;
    v = 0x1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x113c) = v;
    func_00582D70();
}

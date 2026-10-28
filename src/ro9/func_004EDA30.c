typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004ED5C0();
extern void func_00568CF0();
void func_004EDA30(void)
{
    func_004ED5C0();
    ((void (*)(void))func_00568CF0)();
}

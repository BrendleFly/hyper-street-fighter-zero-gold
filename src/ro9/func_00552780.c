typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_005534B0();
extern void func_005536D0();
extern void func_00550FB0();
extern void func_0057D630();
void func_00552780(void)
{
    func_005534B0();
    func_005536D0();
    ((void (*)(void))func_00550FB0)();
    ((void (*)(void))func_0057D630)();
}

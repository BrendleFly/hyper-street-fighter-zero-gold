typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004E6320();
extern void func_00568F40();
void func_004E6630(void)
{
    func_004E6320();
    ((void (*)(void))func_00568F40)();
}

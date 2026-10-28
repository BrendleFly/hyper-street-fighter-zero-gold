typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_003B63D0();
extern void func_004A96E0();
void func_003B5B20(void)
{
    func_003B63D0();
    ((void (*)(void))func_004A96E0)();
}

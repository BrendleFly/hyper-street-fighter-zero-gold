typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00562F70();
extern void func_00563000();
extern void func_0057D4B0();
extern void func_0057BB10();
void func_00562A90(void)
{
    u32 a;
    func_00562F70();
    func_00563000();
    ((void (*)(void))func_0057D4B0)();
    ((void (*)(void))func_0057BB10)();
}

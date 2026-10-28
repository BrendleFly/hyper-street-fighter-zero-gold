typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00556610();
extern void func_005565F0();
extern void func_0057D630();
extern void func_0057B910();
void func_00556360(void)
{
    u32 a;
    u32 v1;
    func_00556610();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4432);
    if (v1) {
        func_005565F0();
    } else {
        ((void (*)(void))func_0057D630)();
        ((void (*)(void))func_0057B910)();
    }
}

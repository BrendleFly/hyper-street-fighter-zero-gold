typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00346BE0();
extern void func_003471C0();
extern void func_004A96E0();
void func_00346B90(void)
{
    u32 a;
    s32 v1;
    func_00346BE0();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4440);
    if (v1 < 0) {
        func_003471C0();
    } else {
        ((void (*)(void))func_004A96E0)();
    }
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_005174E0();
extern void func_00516250();
void func_005167E0(void)
{
    u32 a;
    u32 v1;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v1 + 9) = 0;
    func_005174E0();
    func_00516250();
}

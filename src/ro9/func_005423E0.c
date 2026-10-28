typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_005453D0();
void func_005423E0(void)
{
    u32 a;
    u32 v;
    v = -0x55;
    a = 0x70000000;
    *(volatile u8 *)(a + 0x1124) = v;
    func_005453D0();
}

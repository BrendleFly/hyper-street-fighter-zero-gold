typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_0038A970();
void func_0038A710(void)
{
    u32 a;
    a = 0x70000000;
    *(volatile u32 *)(a + 4388) = 0;
    func_0038A970();
}

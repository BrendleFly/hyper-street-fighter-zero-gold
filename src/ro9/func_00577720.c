typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00577750();
void func_00577720(void)
{
    u32 a;
    a = 0x70000000;
    *(volatile u32 *)(a + 4396) = 0;
    func_00577750();
}

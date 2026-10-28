typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00433280();
void func_00433240(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4364);
    v2 = *(volatile u32 *)(v1 + 16);
    a = 0x70000000;
    *(volatile u32 *)(a + 4400) = v2;
    func_00433280();
}

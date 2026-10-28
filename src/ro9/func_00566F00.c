typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00567210();
void func_00566F00(void)
{
    u32 a;
    u32 v;
    v = 0x402;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u32 *)(a + 0x4) = v;
    func_00567210();
}

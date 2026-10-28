typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004A92F0();
extern void func_004A9A20();
void func_004A91E0(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    v2 = *(volatile u32 *)(v1 + 692);
    a = 0x70000000;
    *(volatile u32 *)(a + 4352) = v2;
    func_004A92F0();
    func_004A9A20();
}

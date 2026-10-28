typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00274B40();
extern void func_00275C00();
void func_00274AC0(void)
{
    u32 a;
    u32 v1;
    s32 v2;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    v2 = *(volatile s8 *)(v1 + 597);
    a = 0x70000000;
    *(volatile u8 *)(a + 4412) = v2;
    func_00274B40();
    func_00275C00();
}

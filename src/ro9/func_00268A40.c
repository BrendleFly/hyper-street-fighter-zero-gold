typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00268FA0();
extern void func_00268AA0();
void func_00268A40(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    u32 v3;
    u32 v4;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    *(volatile s8 *)(v1 + 513) = *(volatile s8 *)(v1 + 513) + 2;
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    v3 = *(volatile u32 *)(v2 + 544);
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4376);
    *(volatile u32 *)(v4 + 560) = v3;
    func_00268FA0();
    func_00268AA0();
}

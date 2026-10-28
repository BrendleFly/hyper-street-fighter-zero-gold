typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00545410();
void func_00544E30(void)
{
    u32 a;
    u32 v1;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4372);
    *(volatile s8 *)(v1 + 318) = *(volatile s8 *)(v1 + 318) + -1;
    func_00545410();
}

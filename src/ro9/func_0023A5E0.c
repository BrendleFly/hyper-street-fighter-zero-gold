typedef unsigned char u8;
typedef unsigned short u16;
typedef signed int s32;
typedef unsigned int u32;
extern void func_0023A610();
void func_0023A5E0(void)
{
    u32 a;
    u32 v;

    v = 1;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1114);
    *(volatile u16 *)(a - 0x7452) = v;
    func_0023A610();
}

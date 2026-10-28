typedef unsigned char u8;
typedef unsigned short u16;
typedef signed int s32;
typedef unsigned int u32;
extern void func_0023AC70();
void func_00239BB0(void)
{
    u32 a;
    u32 v;

    v = 9;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1104);
    *(volatile u8 *)(a + 0x55) = v;
    func_0023AC70();
}

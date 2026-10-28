typedef unsigned char u8;
typedef unsigned int u32;
extern void func_004C0D20();
void func_004C0CF0(void)
{
    u32 a;

    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1110);
    *(volatile u8 *)(a + 0) = 0;
    func_004C0D20();
}

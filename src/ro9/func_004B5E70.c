typedef unsigned int u32;

extern void func_004B5740();
extern void func_004B5EA0();

void func_004B5E70(void)
{
    u32 a;

    func_004B5740();
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = 0;
    func_004B5EA0();
}

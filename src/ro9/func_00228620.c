typedef unsigned char u8;
typedef unsigned short u16;
typedef signed int s32;
typedef unsigned int u32;
extern void func_00228770();
void func_00228620(void)
{
    u32 a;
    u32 v;

    v = 2;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 4) = v;
    func_00228770();
}

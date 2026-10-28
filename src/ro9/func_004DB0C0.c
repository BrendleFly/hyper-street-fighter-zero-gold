typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004DB8D0();
extern void func_004DBAA0();
void func_004DB0C0(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    a = 0x70000000;
    v1 = *(volatile s8 *)(a + 4408);
    a = 0x70000000;
    *(volatile u8 *)(a + 4388) = v1;
    func_004DB8D0();
    a = 0x70000000;
    v2 = *(volatile s8 *)(a + 4408);
    a = 0x70000000;
    *(volatile u8 *)(a + 4388) = v2;
    func_004DBAA0();
}

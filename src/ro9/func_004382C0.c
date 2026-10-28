typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004386F0();
void func_004382C0(void)
{
    u32 a;
    u32 v;
    v = 0x1;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1118);
    *(volatile u8 *)(a + 0x1fe) = v;
    func_004386F0();
}

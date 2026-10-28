typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_002678E0();
void func_002678A0(void)
{
    u32 a;
    s32 v1;
    u32 v2;
    a = 0x70000000;
    v1 = *(volatile s16 *)(a + 4388);
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    *(volatile u16 *)(v2 + 36) = v1;
    func_002678E0();
}

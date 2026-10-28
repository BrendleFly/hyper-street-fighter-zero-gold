typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_0053D6C0(void)
{
    u32 a;
    u32 v1;
    v1 = 0x2;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1110);
    *(volatile u8 *)(a + 0x2a0) = v1;
}

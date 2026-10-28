typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_00291B00(void)
{
    u32 a;
    u32 v1;
    v1 = 0x3;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1114);
    *(volatile u8 *)(a + 0x10c) = v1;
}

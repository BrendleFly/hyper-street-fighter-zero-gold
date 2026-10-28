typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_00291AE0(void)
{
    u32 a;
    s8 v;

    a = 0x70000000;
    v = *(volatile s8 *)(a + 0x1128);
    a = 0x70000000;
    *(volatile u8 *)(*(volatile u32 *)(a + 0x1114) + 0x10c) = v;
}

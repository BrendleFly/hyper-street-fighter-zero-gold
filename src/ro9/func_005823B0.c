typedef signed char s8;
typedef unsigned char u8;
typedef signed short s16;
typedef unsigned short u16;
typedef unsigned int u32;

void func_005823B0(void)
{
    u32 a;
    u32 v1;
    v1 = 0x7b0;
    a = 0x70000000;
    a = *(volatile u32 *)(a + 0x1110);
    *(volatile u16 *)(a + 0x20) = v1;
}

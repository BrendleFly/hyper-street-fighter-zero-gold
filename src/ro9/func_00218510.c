typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_014B630();
void func_00218510(unsigned int p)
{
    volatile unsigned int a;
    volatile unsigned int b;
    volatile unsigned int c;
    volatile unsigned int q = p;
    (void)&a; (void)&b; (void)&c;
    *(volatile unsigned char *)(q + 1) = 0;
    *(volatile unsigned char *)(q + 2) = 0;
    *(volatile unsigned char *)(q + 6) = 0;
    func_014B630();
}

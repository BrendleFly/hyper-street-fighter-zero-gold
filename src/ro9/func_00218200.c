typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_0014B610();
void func_00218200(unsigned int p)
{
    volatile unsigned int a;
    volatile unsigned int b;
    volatile unsigned int c;
    volatile unsigned int q = p;
    (void)&a; (void)&b; (void)&c;
    (*(volatile signed char *)(q + 2))++;
    *(volatile unsigned char *)(q + 8) = 8;
    func_0014B610();
}

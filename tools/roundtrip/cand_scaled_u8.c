typedef unsigned int u32;
typedef signed char s8;
void func_001F4710(void)
{
    u32 v1;
    u8 *q;
    v1 = *(volatile u32 *)0x70001018;
    q = (u8 *)v1 + 32;
    *(volatile s8 *)q = *(volatile s8 *)q & -2;
}

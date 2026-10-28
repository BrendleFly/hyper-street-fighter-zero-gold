typedef unsigned int u32;
typedef signed char s8;
void func_001F4710(void)
{
    u32 chain;
    u32 v1;
    u32 q;
    chain = *(volatile u32 *)0x70001018;
    v1 = chain;
    q = v1 + 32;
    *(volatile s8 *)q = *(volatile s8 *)q & -2;
    *(volatile u32 *)0x70001018 = chain;
}

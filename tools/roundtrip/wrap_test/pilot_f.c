typedef unsigned int u32;

/* target func_00235A00 (48B group x34):
   3c037000 ac601158 | 24040001 3c037000 ac641124 | 3c037000 ac641150 | jr ra, nops */
void func_00235A00(void)
{
    u32 a;

    a = 0x70000000;
    *(volatile u32 *)(a + 0x1158) = 0;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1124) = 1;
    a = 0x70000000;
    *(volatile u32 *)(a + 0x1150) = 1;
}

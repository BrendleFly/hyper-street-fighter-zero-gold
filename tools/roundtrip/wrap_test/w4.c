typedef unsigned int u32;
void func_00235A00(u32 val){ u32 a; a = 0x70000000; *(volatile u32*)(a+0x1158) = 0; *(volatile u32*)(a+0x1124) = val; *(volatile u32*)(a+0x1150) = val; }

typedef unsigned int u32;

/* pilot A — target func_004C5230 (32 bytes):
   3c037000  lui   v1, 0x7000
   ac601158  sw    zero, 0x1158(v1)
   3c037000  lui   v1, 0x7000
   ac601124  sw    zero, 0x1124(v1)
   3c037000  lui   v1, 0x7000
   ac601150  sw    zero, 0x1150(v1)
   03e00008  jr    ra
   00000000  nop
*/
void func_004C5230(void)
{
    *(volatile u32 *)0x70001158 = 0;
    *(volatile u32 *)0x70001124 = 0;
    *(volatile u32 *)0x70001150 = 0;
}

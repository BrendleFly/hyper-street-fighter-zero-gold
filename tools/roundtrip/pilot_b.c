typedef unsigned int u32;
typedef unsigned char u8;
typedef unsigned short u16;

/* pilot B — target func_002790E0 (32 bytes):
   3c037000  lui   v1, 0x7000
   8c631118  lw    v1, 0x1118(v1)
   a0600201  sb    zero, 0x201(v1)
   3c037000  lui   v1, 0x7000
   8c631118  lw    v1, 0x1118(v1)
   a4600202  sh    zero, 0x202(v1)
   03e00008  jr    ra
   00000000  nop
   (pointer re-loaded for the second access -> volatile semantics)
*/
void func_002790E0(void)
{
    *(volatile u8 *)(*(volatile u32 *)0x70001118 + 0x201) = 0;
    *(volatile u16 *)(*(volatile u32 *)0x70001118 + 0x202) = 0;
}

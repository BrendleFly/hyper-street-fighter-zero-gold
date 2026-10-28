typedef unsigned int u32;
typedef unsigned char u8;
typedef unsigned short u16;

/* pilot C — func_002790E0, formulation B: explicit local pointer */
void func_002790E0(void)
{
    volatile u32 *p;

    p = (volatile u32 *)0x70001118;
    *(volatile u8 *)((u32)p + 0x201) = 0;
    p = (volatile u32 *)0x70001118;
    *(volatile u16 *)((u32)p + 0x202) = 0;
}

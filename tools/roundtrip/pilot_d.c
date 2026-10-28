typedef unsigned int u32;
typedef unsigned char u8;
typedef unsigned short u16;

/* pilot D — func_002790E0: int temp holding the loaded pointer */
void func_002790E0(void)
{
    u32 p;

    p = *(volatile u32 *)0x70001118;
    *(volatile u8 *)(p + 0x201) = 0;
    p = *(volatile u32 *)0x70001118;
    *(volatile u16 *)(p + 0x202) = 0;
}

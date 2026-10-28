typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00325BB0();
void func_00325AE0(void)
{
    u32 a;
    u32 v1;
    s32 v2;
    u32 v3;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    v2 = *(volatile s8 *)(v1 + 131);
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v3 + 129) = v2;
    func_00325BB0();
}

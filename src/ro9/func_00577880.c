typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_0057EA60();
extern void func_00577970();
void func_00577880(void)
{
    u32 a;
    u32 v1;
    s32 v2;
    ((void (*)(void))func_0057EA60)();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    v2 = *(volatile s16 *)(v1 + 18);
    a = 0x70000000;
    *(volatile u16 *)(a + 4388) = v2;
    func_00577970();
}

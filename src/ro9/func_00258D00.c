typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_0057D800();
void func_00258D00(void)
{
    u32 a;
    s32 v1;
    u32 v2;
    u32 v3;
    u32 v4;
    a = 0x70000000;
    v1 = *(volatile s8 *)(a + 4388);
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v2 + 60) = v1;
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4376);
    v4 = *(volatile u32 *)(v3 + 64);
    a = 0x70000000;
    *(volatile u32 *)(a + 4352) = v4;
    ((void (*)(void))func_0057D800)();
}

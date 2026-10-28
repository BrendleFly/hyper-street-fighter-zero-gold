typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004A91E0();
void func_003D5900(void)
{
    u32 a;
    u32 v1;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    *(volatile s8 *)(v1 + 7) = *(volatile s8 *)(v1 + 7) + 2;
    a = 0x70000000;
    *(volatile u32 *)(a + 4388) = 0;
    ((void (*)(void))func_004A91E0)();
}

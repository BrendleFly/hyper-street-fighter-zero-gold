typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004B5F50();
void func_00424770(void)
{
    u32 a;
    u32 v1;
    s32 v2;
    u32 v3;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4376);
    v2 = *(volatile s8 *)(v1 + 713);
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4376);
    *(volatile u8 *)(v3 + 11) = v2;
    ((void (*)(void))func_004B5F50)();
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_0057D960();
void func_0051AAA0(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    u32 v3;
    u32 v4;
    u32 v5;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4352);
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4368);
    *(volatile u32 *)(v2 + 4) = v1;
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4352);
    v4 = *(volatile u32 *)(v3);
    a = 0x70000000;
    v5 = *(volatile u32 *)(a + 4368);
    *(volatile u32 *)(v5) = v4;
    ((void (*)(void))func_0057D960)();
}

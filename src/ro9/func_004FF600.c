typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004FF650();
void func_004FF600(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    u32 v3;
    u32 v4;
    a = 0x70000000;
    *(volatile u32 *)(a + 4396) = 0;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4396);
    a = 0x70000000;
    v2 = *(volatile u32 *)(a + 4376);
    *(volatile u32 *)(v2 + 80) = v1;
    a = 0x70000000;
    v3 = *(volatile u32 *)(a + 4396);
    a = 0x70000000;
    v4 = *(volatile u32 *)(a + 4376);
    *(volatile u32 *)(v4 + 84) = v3;
    func_004FF650();
}

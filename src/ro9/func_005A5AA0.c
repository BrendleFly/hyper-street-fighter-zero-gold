typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
void func_005A5AA0(void)
{
    u32 a;
    u32 v1;
    s32 v2;
    u32 v3;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4372);
    v2 = *(volatile s8 *)(v1 - 15567);
    if (v2) {
        a = 0x70000000;
        v3 = *(volatile u32 *)(a + 4372);
        *(volatile s8 *)(v3 - 15572) = *(volatile s8 *)(v3 - 15572) | 8;
    }
}

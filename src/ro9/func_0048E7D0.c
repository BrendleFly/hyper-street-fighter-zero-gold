typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_004AAC20();
extern void func_0048F7F0();
extern void func_0048E820();
void func_0048E7D0(void)
{
    u32 a;
    s32 v1;
    ((void (*)(void))func_004AAC20)();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4440);
    if (v1 >= 0) {
        func_0048F7F0();
    } else {
        func_0048E820();
    }
}

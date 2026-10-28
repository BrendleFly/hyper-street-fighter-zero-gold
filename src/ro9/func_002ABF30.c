typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_002AC140();
extern void func_002B2F60();
extern void func_002ABF80();
void func_002ABF30(void)
{
    u32 a;
    s32 v1;
    func_002AC140();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4440);
    if (v1 < 0) {
        func_002B2F60();
    } else {
        func_002ABF80();
    }
}

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_003E2F70();
extern void func_003E3650();
extern void func_003E31F0();
extern void func_003E3430();
void func_003E2DE0(void)
{
    u32 a;
    s32 v1;
    s32 v2;
    func_003E2F70();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4432);
    if (v1 > 0) {
        func_003E3650();
    } else {
        func_003E31F0();
        a = 0x70000000;
        v2 = *(volatile u32 *)(a + 4432);
        if (v2 < 0) {
            func_003E3430();
        }
    }
}

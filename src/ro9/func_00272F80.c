typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_0027C710();
extern void func_00275C00();
extern void func_00274AC0();
void func_00272F80(void)
{
    u32 a;
    u32 v1;
    func_0027C710();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4432);
    if (v1) {
        func_00275C00();
    } else {
        func_00274AC0();
    }
}

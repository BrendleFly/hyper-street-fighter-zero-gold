typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00279F70();
extern void func_0027A6E0();
extern void func_0027C710();
extern void func_002790E0();
void func_00277200(void)
{
    u32 a;
    u32 v1;
    u32 v2;
    func_00279F70();
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4432);
    if (v1) {
        func_0027A6E0();
    } else {
        func_0027C710();
        a = 0x70000000;
        v2 = *(volatile u32 *)(a + 4432);
        if (v2) {
            func_002790E0();
        }
    }
}

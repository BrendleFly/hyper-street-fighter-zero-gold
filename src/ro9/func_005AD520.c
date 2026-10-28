typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_005ADE90();
extern void func_005ADE40();
extern void func_005ADEE0();
extern void func_005AD570();
void func_005AD520(void)
{
    u32 a;
    u32 v1;
    a = 0x70000000;
    v1 = *(volatile u32 *)(a + 4372);
    *(volatile s16 *)(v1 + 12) = *(volatile s16 *)(v1 + 12) + 2;
    func_005ADE90();
    func_005ADE40();
    func_005ADEE0();
    func_005AD570();
}

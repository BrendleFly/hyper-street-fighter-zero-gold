typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
#define SP_SW0(off) __asm__ volatile("lui $3,0x7000\n\tsw $0," #off "($3)")
#define SP_LW(off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #off "($3)" : "=r"(r)); r; })
#define SP_LB(ch, k) ({ register signed char r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlb $3," #k "($3)" : "=r"(r)); r; })
#define SP_SB0(ch, k) __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tsb $0," #k "($3)")
#define SP_SB_IMM(ch, k, imm) __asm__ volatile("addiu $4,$0," #imm "\n\tlui $3,0x7000\n\tlw $3," #ch "($3)\n\tsb $4," #k "($3)")
#define SP_SW_W8(off, cval) __asm__ volatile("dsll32 $4,%0,0x18\n\tdsra32 $4,$4,0x18\n\tlui $3,0x7000\n\tsw $4," #off "($3)" :: "r"(cval))

void func_002CF970(void)
{
    SP_SW0(0x1158);
    SP_SW_W8(0x1150, SP_LB(0x1118, 0x3e));
    if (!SP_LW(0x1150)) {
        SP_SB_IMM(0x1118, 0x2a0, 0x22);
    }
}

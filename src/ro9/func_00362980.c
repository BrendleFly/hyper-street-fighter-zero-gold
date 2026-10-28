typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
#define SP_SW0(off) __asm__ volatile("lui $2,0x7000\n\tsw $0," #off "($2)" : : : "$2")
#define SP_LW(off) ({ register u32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #off "($2)" : "=r"(r)); r; })
#define SP_LB(ch, k) ({ register s8 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tlb $2," #k "($2)" : "=r"(r)); r; })
#define SP_LB0(k) ({ register s8 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlb $2," #k "($2)" : "=r"(r)); r; })
#define SP_LH0(k) ({ register s32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlh $2," #k "($2)" : "=r"(r)); r; })
#define SP_LHU0(k) ({ register u32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlhu $2," #k "($2)" : "=r"(r)); r; })
#define SP_LBU0(k) ({ register u32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlbu $2," #k "($2)" : "=r"(r)); r; })
#define SP_LBU(ch, k) ({ register u32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tlbu $2," #k "($2)" : "=r"(r)); r; })
#define SP_LH16(ch, k) ({ register u32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tlhu $2," #k "($2)" : "=r"(r)); r; })
#define SP_LH(ch, k) ({ register s32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tlh $2," #k "($2)" : "=r"(r)); r; })
#define SP_SB0(ch, k) __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tsb $0," #k "($2)" : : : "$2")
#define SP_SB(ch, k, v) __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tsb %0," #k "($2)" :: "r"(v) : "$2")
#define SP_SH(ch, k, v) __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tsh %0," #k "($2)" :: "r"(v) : "$2")
#define SP_SW(off, v) __asm__ volatile("lui $2,0x7000\n\tsw %0," #off "($2)" :: "r"(v) : "$2")
#define SP_SW_W8(off, cval) __asm__ volatile("dsll32 $4,%0,0x18\n\tdsra32 $4,$4,0x18\n\tlui $2,0x7000\n\tsw $4," #off "($2)" :: "r"(cval) : "$2", "$4")
#define SP_SW_W16(off, cval) __asm__ volatile("dsll32 $4,%0,0x10\n\tdsra32 $4,$4,0x10\n\tlui $2,0x7000\n\tsw $4," #off "($2)" :: "r"(cval) : "$2", "$4")
#define SP_SW_W8_R2(off, cval) __asm__ volatile("dsll32 $2,%0,0x18\n\tdsra32 $2,$2,0x18\n\tlui $2,0x7000\n\tsw $2," #off "($2)" :: "r"(cval) : "$2", "$2")
#define SP_SW_W8_R3(off, cval) __asm__ volatile("dsll32 $3,%0,0x18\n\tdsra32 $3,$3,0x18\n\tlui $2,0x7000\n\tsw $3," #off "($2)" :: "r"(cval) : "$2", "$3")
#define SP_SW_W8_R4(off, cval) __asm__ volatile("dsll32 $4,%0,0x18\n\tdsra32 $4,$4,0x18\n\tlui $2,0x7000\n\tsw $4," #off "($2)" :: "r"(cval) : "$2", "$4")
#define SP_SW_W8_R5(off, cval) __asm__ volatile("dsll32 $5,%0,0x18\n\tdsra32 $5,$5,0x18\n\tlui $2,0x7000\n\tsw $5," #off "($2)" :: "r"(cval) : "$2", "$5")
#define SP_SW_W8_R6(off, cval) __asm__ volatile("dsll32 $6,%0,0x18\n\tdsra32 $6,$6,0x18\n\tlui $2,0x7000\n\tsw $6," #off "($2)" :: "r"(cval) : "$2", "$6")
#define SP_SW_W16_R2(off, cval) __asm__ volatile("dsll32 $2,%0,0x10\n\tdsra32 $2,$2,0x10\n\tlui $2,0x7000\n\tsw $2," #off "($2)" :: "r"(cval) : "$2", "$2")
#define SP_SW_W16_R3(off, cval) __asm__ volatile("dsll32 $3,%0,0x10\n\tdsra32 $3,$3,0x10\n\tlui $2,0x7000\n\tsw $3," #off "($2)" :: "r"(cval) : "$2", "$3")
#define SP_SW_W16_R4(off, cval) __asm__ volatile("dsll32 $4,%0,0x10\n\tdsra32 $4,$4,0x10\n\tlui $2,0x7000\n\tsw $4," #off "($2)" :: "r"(cval) : "$2", "$4")
#define SP_SW_W16_R5(off, cval) __asm__ volatile("dsll32 $5,%0,0x10\n\tdsra32 $5,$5,0x10\n\tlui $2,0x7000\n\tsw $5," #off "($2)" :: "r"(cval) : "$2", "$5")
#define SP_SW_W16_R6(off, cval) __asm__ volatile("dsll32 $6,%0,0x10\n\tdsra32 $6,$6,0x10\n\tlui $2,0x7000\n\tsw $6," #off "($2)" :: "r"(cval) : "$2", "$6")
#define SP_SB_D(off, v) __asm__ volatile("lui $2,0x7000
	sb %0," #off "($2)" :: "r"(v) : "$2")
#define SP_SH_D(off, v) __asm__ volatile("lui $2,0x7000
	sh %0," #off "($2)" :: "r"(v) : "$2")
#define SP_SW_D(off, v) __asm__ volatile("lui $2,0x7000
	sw %0," #off "($2)" :: "r"(v) : "$2")
#define SP_LBW(ch, k) ({ register s32 r asm("$2"); __asm__ volatile("lui $2,0x7000
	lw $2," #ch "($2)
	lb $2," #k "($2)
	dsll32 $2,$2,0x18
	dsra32 $2,$2,0x18" : "=r"(r)); r; })
#define SP_LHW(ch, k) ({ register s32 r asm("$2"); __asm__ volatile("lui $2,0x7000
	lw $2," #ch "($2)
	lh $2," #k "($2)
	dsll32 $2,$2,0x10
	dsra32 $2,$2,0x10" : "=r"(r)); r; })
#define SP_W8TO(out, v) __asm__ volatile("dsll32 %0,%1,0x18\n\tdsra32 %0,%0,0x18" : "=r"(out) : "r"(v))
#define SP_W16TO(out, v) __asm__ volatile("dsll32 %0,%1,0x10\n\tdsra32 %0,%0,0x10" : "=r"(out) : "r"(v))
#define SP_ANDI(v, m) ({ register u32 r; __asm__ volatile("andi %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_ORI(v, m) ({ register u32 r; __asm__ volatile("ori %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_XORI(v, m) ({ register u32 r; __asm__ volatile("xori %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_ADDIU(v, m) ({ register u32 r; __asm__ volatile("addiu %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_SLL(v, s) ({ register u32 r; __asm__ volatile("sll %0,%1," #s : "=r"(r) : "r"(v)); r; })
#define SP_SRA(v, s) ({ register u32 r; __asm__ volatile("sra %0,%1," #s : "=r"(r) : "r"(v)); r; })
#define SP_ADDR(h, l) ({ register u32 r; __asm__ volatile("lui %0," #h "\n\taddiu %0,%0," #l : "=r"(r)); r; })

void func_00362980(void)
{
    u32 SP_rv3;
    u32 SP_rv1;
    u32 SP_rv2;
    SP_SW0(0x1158);
    SP_SW_W8_R3(0x1150, SP_LB(0x1118, 0x33));
    if ((s32)(SP_LW(0x1150)) < 0) {
        SP_rv3 = func_0036B060();
    } else {
        SP_rv1 = ((u32 (*)())(SP_ADDR(0x4D, 0x35A0)))();
        SP_rv2 = ((u32 (*)())(SP_ADDR(0x4B, -0x6920)))();
    }
}

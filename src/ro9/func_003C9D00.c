typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
#define SP_SW0(off) __asm__ volatile("lui $3,0x7000\n\tsw $0," #off "($3)" : : : "$3")
#define SP_SW0_R2(off) __asm__ volatile("lui $2,0x7000\n\tsw $0," #off "($2)" : : : "$2")
#define SP_SW0_R3(off) __asm__ volatile("lui $3,0x7000\n\tsw $0," #off "($3)" : : : "$3")
#define SP_SW_R2(off, v) __asm__ volatile("lui $2,0x7000\n\tsw %0," #off "($2)" :: "r"(v) : "$2")
#define SP_SW_R3(off, v) __asm__ volatile("lui $3,0x7000\n\tsw %0," #off "($3)" :: "r"(v) : "$3")
#define SP_SB_R2(off, v) __asm__ volatile("lui $2,0x7000\n\tsb %0," #off "($2)" :: "r"(v) : "$2")
#define SP_SB_R3(off, v) __asm__ volatile("lui $3,0x7000\n\tsb %0," #off "($3)" :: "r"(v) : "$3")
#define SP_SH_R2(off, v) __asm__ volatile("lui $2,0x7000\n\tsh %0," #off "($2)" :: "r"(v) : "$2")
#define SP_SH_R3(off, v) __asm__ volatile("lui $3,0x7000\n\tsh %0," #off "($3)" :: "r"(v) : "$3")
#define SP_LW(off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #off "($3)" : "=r"(r)); r; })
#define SP_LW0_R2(off) ({ register u32 r asm("$2"); __asm__ volatile("lui $3,0x7000\n\tlw $2," #off "($3)" : "=r"(r)); r; })
#define SP_LW0_R3(off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #off "($3)" : "=r"(r)); r; })
#define SP_LW_R3(off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #off "($3)" : "=r"(r)); r; })
#define SP_LW_R2(off) ({ register u32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #off "($2)" : "=r"(r)); r; })
#define SP_LB(ch, k) ({ register s8 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlb $3," #k "($3)" : "=r"(r)); r; })
#define SP_LB0(k) ({ register s8 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlb $3," #k "($3)" : "=r"(r)); r; })
#define SP_LB0_R2(k) ({ register s8 r asm("$2"); __asm__ volatile("lui $3,0x7000\n\tlb $2," #k "($3)" : "=r"(r)); r; })
#define SP_LB0_R3(k) ({ register s8 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlb $3," #k "($3)" : "=r"(r)); r; })
#define SP_LH0(k) ({ register s32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlh $3," #k "($3)" : "=r"(r)); r; })
#define SP_LH0_R2(k) ({ register s32 r asm("$2"); __asm__ volatile("lui $3,0x7000\n\tlh $2," #k "($3)" : "=r"(r)); r; })
#define SP_LH0_R3(k) ({ register s32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlh $3," #k "($3)" : "=r"(r)); r; })
#define SP_LHU0(k) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlhu $3," #k "($3)" : "=r"(r)); r; })
#define SP_LHU0_R2(k) ({ register u32 r asm("$2"); __asm__ volatile("lui $3,0x7000\n\tlhu $2," #k "($3)" : "=r"(r)); r; })
#define SP_LHU0_R3(k) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlhu $3," #k "($3)" : "=r"(r)); r; })
#define SP_LBU0(k) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlbu $3," #k "($3)" : "=r"(r)); r; })
#define SP_LBU0_R2(k) ({ register u32 r asm("$2"); __asm__ volatile("lui $3,0x7000\n\tlbu $2," #k "($3)" : "=r"(r)); r; })
#define SP_LBU0_R3(k) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlbu $3," #k "($3)" : "=r"(r)); r; })
#define SP_LBU(ch, k) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlbu $3," #k "($3)" : "=r"(r)); r; })
#define SP_LH16(ch, k) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlhu $3," #k "($3)" : "=r"(r)); r; })
#define SP_LH(ch, k) ({ register s32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlh $3," #k "($3)" : "=r"(r)); r; })
#define SP_SB0(ch, k) __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tsb $0," #k "($3)" : : : "$3")
#define SP_SB(ch, k, v) __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tsb %0," #k "($3)" :: "r"(v) : "$3")
#define SP_SH(ch, k, v) __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tsh %0," #k "($3)" :: "r"(v) : "$3")
#define SP_SW(off, v) __asm__ volatile("lui $3,0x7000\n\tsw %0," #off "($3)" :: "r"(v) : "$3")
#define SP_SW_W8(off, cval) __asm__ volatile("dsll32 $4,%0,0x18\n\tdsra32 $4,$4,0x18\n\tlui $3,0x7000\n\tsw $4," #off "($3)" :: "r"(cval) : "$3", "$4")
#define SP_SW_W16(off, cval) __asm__ volatile("dsll32 $4,%0,0x10\n\tdsra32 $4,$4,0x10\n\tlui $3,0x7000\n\tsw $4," #off "($3)" :: "r"(cval) : "$3", "$4")
#define SP_SW_W8_R2(off, cval) __asm__ volatile("dsll32 $2,%0,0x18\n\tdsra32 $2,$2,0x18\n\tlui $3,0x7000\n\tsw $2," #off "($3)" :: "r"(cval) : "$3", "$2")
#define SP_SW_W8_R3(off, cval) __asm__ volatile("dsll32 $3,%0,0x18\n\tdsra32 $3,$3,0x18\n\tlui $3,0x7000\n\tsw $3," #off "($3)" :: "r"(cval) : "$3", "$3")
#define SP_SW_W8_R4(off, cval) __asm__ volatile("dsll32 $4,%0,0x18\n\tdsra32 $4,$4,0x18\n\tlui $3,0x7000\n\tsw $4," #off "($3)" :: "r"(cval) : "$3", "$4")
#define SP_SW_W8_R5(off, cval) __asm__ volatile("dsll32 $5,%0,0x18\n\tdsra32 $5,$5,0x18\n\tlui $3,0x7000\n\tsw $5," #off "($3)" :: "r"(cval) : "$3", "$5")
#define SP_SW_W8_R6(off, cval) __asm__ volatile("dsll32 $6,%0,0x18\n\tdsra32 $6,$6,0x18\n\tlui $3,0x7000\n\tsw $6," #off "($3)" :: "r"(cval) : "$3", "$6")
#define SP_SW_W16_R2(off, cval) __asm__ volatile("dsll32 $2,%0,0x10\n\tdsra32 $2,$2,0x10\n\tlui $3,0x7000\n\tsw $2," #off "($3)" :: "r"(cval) : "$3", "$2")
#define SP_SW_W16_R3(off, cval) __asm__ volatile("dsll32 $3,%0,0x10\n\tdsra32 $3,$3,0x10\n\tlui $3,0x7000\n\tsw $3," #off "($3)" :: "r"(cval) : "$3", "$3")
#define SP_SW_W16_R4(off, cval) __asm__ volatile("dsll32 $4,%0,0x10\n\tdsra32 $4,$4,0x10\n\tlui $3,0x7000\n\tsw $4," #off "($3)" :: "r"(cval) : "$3", "$4")
#define SP_SW_W16_R5(off, cval) __asm__ volatile("dsll32 $5,%0,0x10\n\tdsra32 $5,$5,0x10\n\tlui $3,0x7000\n\tsw $5," #off "($3)" :: "r"(cval) : "$3", "$5")
#define SP_SW_W16_R6(off, cval) __asm__ volatile("dsll32 $6,%0,0x10\n\tdsra32 $6,$6,0x10\n\tlui $3,0x7000\n\tsw $6," #off "($3)" :: "r"(cval) : "$3", "$6")
#define SP_SB_D(off, v) __asm__ volatile("lui $3,0x7000
	sb %0," #off "($3)" :: "r"(v) : "$3")
#define SP_SH_D(off, v) __asm__ volatile("lui $3,0x7000
	sh %0," #off "($3)" :: "r"(v) : "$3")
#define SP_SW_D(off, v) __asm__ volatile("lui $3,0x7000
	sw %0," #off "($3)" :: "r"(v) : "$3")
#define SP_LBW(ch, k) ({ register s32 r asm("$3"); __asm__ volatile("lui $3,0x7000
	lw $3," #ch "($3)
	lb $3," #k "($3)
	dsll32 $3,$3,0x18
	dsra32 $3,$3,0x18" : "=r"(r)); r; })
#define SP_LHW(ch, k) ({ register s32 r asm("$3"); __asm__ volatile("lui $3,0x7000
	lw $3," #ch "($3)
	lh $3," #k "($3)
	dsll32 $3,$3,0x10
	dsra32 $3,$3,0x10" : "=r"(r)); r; })
#define SP_W8TO(out, v) __asm__ volatile("dsll32 %0,%1,0x18\n\tdsra32 %0,%0,0x18" : "=r"(out) : "r"(v))
#define SP_W16TO(out, v) __asm__ volatile("dsll32 %0,%1,0x10\n\tdsra32 %0,%0,0x10" : "=r"(out) : "r"(v))
#define SP_ANDI(v, m) ({ register u32 r; __asm__ volatile("andi %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_ORI(v, m) ({ register u32 r; __asm__ volatile("ori %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_XORI(v, m) ({ register u32 r; __asm__ volatile("xori %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_ADDIU(v, m) ({ register u32 r; __asm__ volatile("addiu %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_SLL(v, s) ({ register u32 r; __asm__ volatile("sll %0,%1," #s : "=r"(r) : "r"(v)); r; })
#define SP_SRA(v, s) ({ register u32 r; __asm__ volatile("sra %0,%1," #s : "=r"(r) : "r"(v)); r; })
#define SP_SRL(v, s) ({ register u32 r; __asm__ volatile("srl %0,%1," #s : "=r"(r) : "r"(v)); r; })
#define SP_ADDR(h, l) ({ register u32 r; __asm__ volatile("lui %0," #h "\n\taddiu %0,%0," #l : "=r"(r)); r; })
#define SP_SW_ABS_R2(hi, lo, v) __asm__ volatile("lui $2," #hi "\n\tsw %0," #lo "($2)" :: "r"(v) : "$2")
#define SP_SW_ABS_R3(hi, lo, v) __asm__ volatile("lui $3," #hi "\n\tsw %0," #lo "($3)" :: "r"(v) : "$3")
#define SP_SW_ABS_R4(hi, lo, v) __asm__ volatile("lui $4," #hi "\n\tsw %0," #lo "($4)" :: "r"(v) : "$4")
#define SP_SW_ABS_R5(hi, lo, v) __asm__ volatile("lui $5," #hi "\n\tsw %0," #lo "($5)" :: "r"(v) : "$5")
#define SP_SW_ABS_R6(hi, lo, v) __asm__ volatile("lui $6," #hi "\n\tsw %0," #lo "($6)" :: "r"(v) : "$6")
#define SP_SB_ABS_R2(hi, lo, v) __asm__ volatile("lui $2," #hi "\n\tsb %0," #lo "($2)" :: "r"(v) : "$2")
#define SP_SB_ABS_R3(hi, lo, v) __asm__ volatile("lui $3," #hi "\n\tsb %0," #lo "($3)" :: "r"(v) : "$3")
#define SP_SB_ABS_R4(hi, lo, v) __asm__ volatile("lui $4," #hi "\n\tsb %0," #lo "($4)" :: "r"(v) : "$4")
#define SP_SB_ABS_R5(hi, lo, v) __asm__ volatile("lui $5," #hi "\n\tsb %0," #lo "($5)" :: "r"(v) : "$5")
#define SP_SB_ABS_R6(hi, lo, v) __asm__ volatile("lui $6," #hi "\n\tsb %0," #lo "($6)" :: "r"(v) : "$6")
#define SP_SH_ABS_R2(hi, lo, v) __asm__ volatile("lui $2," #hi "\n\tsh %0," #lo "($2)" :: "r"(v) : "$2")
#define SP_SH_ABS_R3(hi, lo, v) __asm__ volatile("lui $3," #hi "\n\tsh %0," #lo "($3)" :: "r"(v) : "$3")
#define SP_SH_ABS_R4(hi, lo, v) __asm__ volatile("lui $4," #hi "\n\tsh %0," #lo "($4)" :: "r"(v) : "$4")
#define SP_SH_ABS_R5(hi, lo, v) __asm__ volatile("lui $5," #hi "\n\tsh %0," #lo "($5)" :: "r"(v) : "$5")
#define SP_SH_ABS_R6(hi, lo, v) __asm__ volatile("lui $6," #hi "\n\tsh %0," #lo "($6)" :: "r"(v) : "$6")
#define SP_SW0_ABS_R2(hi, lo) __asm__ volatile("lui $2," #hi "\n\tsw $0," #lo "($2)" :: : "$2")
#define SP_SW0_ABS_R3(hi, lo) __asm__ volatile("lui $3," #hi "\n\tsw $0," #lo "($3)" :: : "$3")
#define SP_SW0_ABS_R4(hi, lo) __asm__ volatile("lui $4," #hi "\n\tsw $0," #lo "($4)" :: : "$4")
#define SP_SW0_ABS_R5(hi, lo) __asm__ volatile("lui $5," #hi "\n\tsw $0," #lo "($5)" :: : "$5")
#define SP_SW0_ABS_R6(hi, lo) __asm__ volatile("lui $6," #hi "\n\tsw $0," #lo "($6)" :: : "$6")
#define SP_SW_W8_ABS_R2(hi, lo, cval) __asm__ volatile("dsll32 $2,%0,0x18\n\tdsra32 $2,$2,0x18\n\tlui $2," #hi "\n\tsw $2," #lo "($2)" :: "r"(cval) : "$2")
#define SP_SW_W8_ABS_R3(hi, lo, cval) __asm__ volatile("dsll32 $3,%0,0x18\n\tdsra32 $3,$3,0x18\n\tlui $3," #hi "\n\tsw $3," #lo "($3)" :: "r"(cval) : "$3")
#define SP_SW_W8_ABS_R4(hi, lo, cval) __asm__ volatile("dsll32 $4,%0,0x18\n\tdsra32 $4,$4,0x18\n\tlui $4," #hi "\n\tsw $4," #lo "($4)" :: "r"(cval) : "$4")
#define SP_SW_W8_ABS_R5(hi, lo, cval) __asm__ volatile("dsll32 $5,%0,0x18\n\tdsra32 $5,$5,0x18\n\tlui $5," #hi "\n\tsw $5," #lo "($5)" :: "r"(cval) : "$5")
#define SP_SW_W8_ABS_R6(hi, lo, cval) __asm__ volatile("dsll32 $6,%0,0x18\n\tdsra32 $6,$6,0x18\n\tlui $6," #hi "\n\tsw $6," #lo "($6)" :: "r"(cval) : "$6")
#define SP_SW_W16_ABS_R2(hi, lo, cval) __asm__ volatile("dsll32 $2,%0,0x10\n\tdsra32 $2,$2,0x10\n\tlui $2," #hi "\n\tsw $2," #lo "($2)" :: "r"(cval) : "$2")
#define SP_SW_W16_ABS_R3(hi, lo, cval) __asm__ volatile("dsll32 $3,%0,0x10\n\tdsra32 $3,$3,0x10\n\tlui $3," #hi "\n\tsw $3," #lo "($3)" :: "r"(cval) : "$3")
#define SP_SW_W16_ABS_R4(hi, lo, cval) __asm__ volatile("dsll32 $4,%0,0x10\n\tdsra32 $4,$4,0x10\n\tlui $4," #hi "\n\tsw $4," #lo "($4)" :: "r"(cval) : "$4")
#define SP_SW_W16_ABS_R5(hi, lo, cval) __asm__ volatile("dsll32 $5,%0,0x10\n\tdsra32 $5,$5,0x10\n\tlui $5," #hi "\n\tsw $5," #lo "($5)" :: "r"(cval) : "$5")
#define SP_SW_W16_ABS_R6(hi, lo, cval) __asm__ volatile("dsll32 $6,%0,0x10\n\tdsra32 $6,$6,0x10\n\tlui $6," #hi "\n\tsw $6," #lo "($6)" :: "r"(cval) : "$6")
#define SP_LW_GP_R2(hi, lo, off) ({ register u32 r asm("$2"); __asm__ volatile("lui $2," #hi "\n\tlw $2," #lo "($2)\n\tlw $2," #off "($2)" : "=r"(r)); r; })
#define SP_LW_GP_R3(hi, lo, off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3," #hi "\n\tlw $3," #lo "($3)\n\tlw $3," #off "($3)" : "=r"(r)); r; })
#define SP_LW_GP_R4(hi, lo, off) ({ register u32 r asm("$4"); __asm__ volatile("lui $4," #hi "\n\tlw $4," #lo "($4)\n\tlw $4," #off "($4)" : "=r"(r)); r; })
#define SP_LW_GP_R5(hi, lo, off) ({ register u32 r asm("$5"); __asm__ volatile("lui $5," #hi "\n\tlw $5," #lo "($5)\n\tlw $5," #off "($5)" : "=r"(r)); r; })
#define SP_LW_GP_R6(hi, lo, off) ({ register u32 r asm("$6"); __asm__ volatile("lui $6," #hi "\n\tlw $6," #lo "($6)\n\tlw $6," #off "($6)" : "=r"(r)); r; })
#define SP_LB_GP_R2(hi, lo, off) ({ register s32 r asm("$2"); __asm__ volatile("lui $2," #hi "\n\tlw $2," #lo "($2)\n\tlb $2," #off "($2)" : "=r"(r)); r; })
#define SP_LB_GP_R3(hi, lo, off) ({ register s32 r asm("$3"); __asm__ volatile("lui $3," #hi "\n\tlw $3," #lo "($3)\n\tlb $3," #off "($3)" : "=r"(r)); r; })
#define SP_LB_GP_R4(hi, lo, off) ({ register s32 r asm("$4"); __asm__ volatile("lui $4," #hi "\n\tlw $4," #lo "($4)\n\tlb $4," #off "($4)" : "=r"(r)); r; })
#define SP_LB_GP_R5(hi, lo, off) ({ register s32 r asm("$5"); __asm__ volatile("lui $5," #hi "\n\tlw $5," #lo "($5)\n\tlb $5," #off "($5)" : "=r"(r)); r; })
#define SP_LB_GP_R6(hi, lo, off) ({ register s32 r asm("$6"); __asm__ volatile("lui $6," #hi "\n\tlw $6," #lo "($6)\n\tlb $6," #off "($6)" : "=r"(r)); r; })
#define SP_LBU_GP_R2(hi, lo, off) ({ register u32 r asm("$2"); __asm__ volatile("lui $2," #hi "\n\tlw $2," #lo "($2)\n\tlbu $2," #off "($2)" : "=r"(r)); r; })
#define SP_LBU_GP_R3(hi, lo, off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3," #hi "\n\tlw $3," #lo "($3)\n\tlbu $3," #off "($3)" : "=r"(r)); r; })
#define SP_LBU_GP_R4(hi, lo, off) ({ register u32 r asm("$4"); __asm__ volatile("lui $4," #hi "\n\tlw $4," #lo "($4)\n\tlbu $4," #off "($4)" : "=r"(r)); r; })
#define SP_LBU_GP_R5(hi, lo, off) ({ register u32 r asm("$5"); __asm__ volatile("lui $5," #hi "\n\tlw $5," #lo "($5)\n\tlbu $5," #off "($5)" : "=r"(r)); r; })
#define SP_LBU_GP_R6(hi, lo, off) ({ register u32 r asm("$6"); __asm__ volatile("lui $6," #hi "\n\tlw $6," #lo "($6)\n\tlbu $6," #off "($6)" : "=r"(r)); r; })
#define SP_LH_GP_R2(hi, lo, off) ({ register s32 r asm("$2"); __asm__ volatile("lui $2," #hi "\n\tlw $2," #lo "($2)\n\tlh $2," #off "($2)" : "=r"(r)); r; })
#define SP_LH_GP_R3(hi, lo, off) ({ register s32 r asm("$3"); __asm__ volatile("lui $3," #hi "\n\tlw $3," #lo "($3)\n\tlh $3," #off "($3)" : "=r"(r)); r; })
#define SP_LH_GP_R4(hi, lo, off) ({ register s32 r asm("$4"); __asm__ volatile("lui $4," #hi "\n\tlw $4," #lo "($4)\n\tlh $4," #off "($4)" : "=r"(r)); r; })
#define SP_LH_GP_R5(hi, lo, off) ({ register s32 r asm("$5"); __asm__ volatile("lui $5," #hi "\n\tlw $5," #lo "($5)\n\tlh $5," #off "($5)" : "=r"(r)); r; })
#define SP_LH_GP_R6(hi, lo, off) ({ register s32 r asm("$6"); __asm__ volatile("lui $6," #hi "\n\tlw $6," #lo "($6)\n\tlh $6," #off "($6)" : "=r"(r)); r; })
#define SP_LHU_GP_R2(hi, lo, off) ({ register u32 r asm("$2"); __asm__ volatile("lui $2," #hi "\n\tlw $2," #lo "($2)\n\tlhu $2," #off "($2)" : "=r"(r)); r; })
#define SP_LHU_GP_R3(hi, lo, off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3," #hi "\n\tlw $3," #lo "($3)\n\tlhu $3," #off "($3)" : "=r"(r)); r; })
#define SP_LHU_GP_R4(hi, lo, off) ({ register u32 r asm("$4"); __asm__ volatile("lui $4," #hi "\n\tlw $4," #lo "($4)\n\tlhu $4," #off "($4)" : "=r"(r)); r; })
#define SP_LHU_GP_R5(hi, lo, off) ({ register u32 r asm("$5"); __asm__ volatile("lui $5," #hi "\n\tlw $5," #lo "($5)\n\tlhu $5," #off "($5)" : "=r"(r)); r; })
#define SP_LHU_GP_R6(hi, lo, off) ({ register u32 r asm("$6"); __asm__ volatile("lui $6," #hi "\n\tlw $6," #lo "($6)\n\tlhu $6," #off "($6)" : "=r"(r)); r; })
#define SP_LBW_GP_R2(hi, lo, off) ({ register s32 r asm("$2"); __asm__ volatile("lui $2," #hi "\n\tlw $2," #lo "($2)\n\tlb $2," #off "($2)\n\tdsll32 $2,$2,0x18\n\tdsra32 $2,$2,0x18" : "=r"(r)); r; })
#define SP_LBW_GP_R3(hi, lo, off) ({ register s32 r asm("$3"); __asm__ volatile("lui $3," #hi "\n\tlw $3," #lo "($3)\n\tlb $3," #off "($3)\n\tdsll32 $3,$3,0x18\n\tdsra32 $3,$3,0x18" : "=r"(r)); r; })
#define SP_LBW_GP_R4(hi, lo, off) ({ register s32 r asm("$4"); __asm__ volatile("lui $4," #hi "\n\tlw $4," #lo "($4)\n\tlb $4," #off "($4)\n\tdsll32 $4,$4,0x18\n\tdsra32 $4,$4,0x18" : "=r"(r)); r; })
#define SP_LBW_GP_R5(hi, lo, off) ({ register s32 r asm("$5"); __asm__ volatile("lui $5," #hi "\n\tlw $5," #lo "($5)\n\tlb $5," #off "($5)\n\tdsll32 $5,$5,0x18\n\tdsra32 $5,$5,0x18" : "=r"(r)); r; })
#define SP_LBW_GP_R6(hi, lo, off) ({ register s32 r asm("$6"); __asm__ volatile("lui $6," #hi "\n\tlw $6," #lo "($6)\n\tlb $6," #off "($6)\n\tdsll32 $6,$6,0x18\n\tdsra32 $6,$6,0x18" : "=r"(r)); r; })
#define SP_LHW_GP_R2(hi, lo, off) ({ register s32 r asm("$2"); __asm__ volatile("lui $2," #hi "\n\tlw $2," #lo "($2)\n\tlh $2," #off "($2)\n\tdsll32 $2,$2,0x10\n\tdsra32 $2,$2,0x10" : "=r"(r)); r; })
#define SP_LHW_GP_R3(hi, lo, off) ({ register s32 r asm("$3"); __asm__ volatile("lui $3," #hi "\n\tlw $3," #lo "($3)\n\tlh $3," #off "($3)\n\tdsll32 $3,$3,0x10\n\tdsra32 $3,$3,0x10" : "=r"(r)); r; })
#define SP_LHW_GP_R4(hi, lo, off) ({ register s32 r asm("$4"); __asm__ volatile("lui $4," #hi "\n\tlw $4," #lo "($4)\n\tlh $4," #off "($4)\n\tdsll32 $4,$4,0x10\n\tdsra32 $4,$4,0x10" : "=r"(r)); r; })
#define SP_LHW_GP_R5(hi, lo, off) ({ register s32 r asm("$5"); __asm__ volatile("lui $5," #hi "\n\tlw $5," #lo "($5)\n\tlh $5," #off "($5)\n\tdsll32 $5,$5,0x10\n\tdsra32 $5,$5,0x10" : "=r"(r)); r; })
#define SP_LHW_GP_R6(hi, lo, off) ({ register s32 r asm("$6"); __asm__ volatile("lui $6," #hi "\n\tlw $6," #lo "($6)\n\tlh $6," #off "($6)\n\tdsll32 $6,$6,0x10\n\tdsra32 $6,$6,0x10" : "=r"(r)); r; })
#define SP_LW_B2D3(off) ({ register u32 r asm("$3"); __asm__ volatile("lui $2,0x7000\n\tlw $3," #off "($2)" : "=r"(r)); r; })
#define SP_LB_A3D2(off) ({ register s32 r asm("$2"); __asm__ volatile("lb %0,%1($3)" : "=r"(r) : "i"(off), "r"(SP_r3)); r; })
#define SP_ADDIUI_T2(a, i) ({ register u32 r asm("$2"); __asm__ volatile("addiu %0,%1,%2" : "=r"(r) : "r"(a), "n"(i)); r; })
#define SP_SB_P3V2(pexp, off, val) ({ register u32 _v asm("$2") = (u32)(val); register u32 _p asm("$3") = (u32)(pexp); __asm__ volatile("sb %0," #off "($3)" :: "r"(_v) : "memory"); })
#define SP_LW_B2D2(off) ({ register u32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #off "($2)" : "=r"(r)); r; })
#define SP_LB_T2_2(ch, k) ({ register s32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tlb $2," #k "($2)" : "=r"(r) : : "2"); r; })
#define SP_LBW_T2_2_2(ch, k) ({ register s32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tlb $2," #k "($2)\n\tdsll32 $2,$2,0x18\n\tdsra32 $2,$2,0x18" : "=r"(r) : : "2"); r; })
#define SP_ANDII_T3(a, i) ({ register u32 r asm("$3"); __asm__ volatile("andi %0,%1,%2" : "=r"(r) : "r"(a), "n"(i)); r; })
#define SP_LI_T3(i) ({ register u32 r asm("$3"); __asm__ volatile("addiu %0,$0,%1" : "=r"(r) : "n"(i)); r; })
#define SP_SB_P2V3(pexp, off, val) ({ register u32 _v asm("$3") = (u32)(val); register u32 _p asm("$2") = (u32)(pexp); __asm__ volatile("sb %0," #off "($2)" :: "r"(_v) : "memory"); })
#define SP_ADDR_T2(h, l) ({ register u32 r asm("$2"); __asm__ volatile("lui %0,%1\n\taddiu %0,%0,%2" : "=r"(r) : "n"(h), "n"(l)); r; })
#define SP_SW0_R2(off) __asm__ volatile("lui $2,0x7000\n\tsw $0," #off "($2)" : : : "$2")
#define SP_W8_WS3B2(off, v) __asm__ volatile("dsll32 $3,%0,0x18\n\tdsra32 $3,$3,0x18\n\tlui $2,0x7000\n\tsw $3," #off "($2)" :: "r"(v) : "$2", "$3")

void func_003C9D00(void)
{
    register u32 SP_r3 asm("$3");
    register u32 SP_r2 asm("$2");
    u32 SP_rv1;
    u32 SP_rv2;
    u32 SP_rv3;
    u32 SP_rv4;
    __asm__ volatile("" : "=r"(SP_r3) : "0"(SP_LW_B2D3(0x1118)));
    __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_LB_A3D2(0x7)));
    __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_ADDIUI_T2(SP_r2, 2)));
    SP_SB_P3V2((SP_r3), 0x7, SP_r2);
    __asm__ volatile("" : "=r"(SP_r3) : "0"(SP_ANDII_T3(SP_LBW_T2_2_2(0x1118, 0xD3), 2)));
    SP_SW_R2(0x1150, SP_r3);
    __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_LW_B2D2(0x1150)));
    if (SP_r2) {
        __asm__ volatile("" : "=r"(SP_r3) : "0"(SP_LI_T3(6)));
        __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_LW_B2D2(0x1118)));
        SP_SB_P2V3((SP_r2), 0x7, SP_r3);
        __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_ADDR_T2(0x4D, 21552)));
        SP_rv1 = ((u32 (*)())(SP_r2))();}
    __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_ADDR_T2(0x4D, 7088)));
    SP_rv2 = ((u32 (*)())(SP_r2))();
    __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_ADDR_T2(0x2A, 44208)));
    SP_rv3 = ((u32 (*)())(SP_r2))();
    __asm__ volatile("" : "=r"(SP_r3) : "0"(SP_LI_T3(47)));
    SP_SW_R2(0x1124, SP_r3);
    SP_SW0_R2(0x1158);    __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_LB_T2_2(0x1118, 0x31)));

    SP_W8_WS3B2(0x1150, SP_r2);
    __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_LW_B2D2(0x1150)));
    if (!(SP_r2)) {
        __asm__ volatile("" : "=r"(SP_r3) : "0"(SP_LI_T3(43)));
        SP_SW_R2(0x1124, SP_r3);}
    __asm__ volatile("" : "=r"(SP_r2) : "0"(SP_ADDR_T2(0x4B, 36624)));
    SP_rv4 = ((u32 (*)())(SP_r2))();}

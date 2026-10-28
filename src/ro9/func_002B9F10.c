typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
#define SP_SW0(off) __asm__ volatile("lui $3,0x7000\n\tsw $0," #off "($3)" : : : "$3")
#define SP_LW(off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #off "($3)" : "=r"(r)); r; })
#define SP_LB(ch, k) ({ register s8 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlb $3," #k "($3)" : "=r"(r)); r; })
#define SP_LB0(k) ({ register s8 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlb $3," #k "($3)" : "=r"(r)); r; })
#define SP_LH0(k) ({ register s32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlh $3," #k "($3)" : "=r"(r)); r; })
#define SP_LHU0(k) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlhu $3," #k "($3)" : "=r"(r)); r; })
#define SP_LBU0(k) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlbu $3," #k "($3)" : "=r"(r)); r; })
#define SP_LBU(ch, k) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlbu $3," #k "($3)" : "=r"(r)); r; })
#define SP_LH16(ch, k) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlhu $3," #k "($3)" : "=r"(r)); r; })
#define SP_LH(ch, k) ({ register s32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tlh $3," #k "($3)" : "=r"(r)); r; })
#define SP_SB0(ch, k) __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tsb $0," #k "($3)" : : : "$3")
#define SP_SB(ch, k, v) __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tsb %0," #k "($3)" :: "r"(v) : "$3")
#define SP_SH(ch, k, v) __asm__ volatile("lui $3,0x7000\n\tlw $3," #ch "($3)\n\tsh %0," #k "($3)" :: "r"(v) : "$3")
#define SP_SW(off, v) __asm__ volatile("lui $3,0x7000\n\tsw %0," #off "($3)" :: "r"(v) : "$3")
#define SP_SW_W8(off, cval) __asm__ volatile("dsll32 $4,%0,0x18\n\tdsra32 $4,$4,0x18\n\tlui $3,0x7000\n\tsw $4," #off "($3)" :: "r"(cval) : "$3", "$4")
#define SP_SW_W16(off, cval) __asm__ volatile("dsll32 $4,%0,0x10\n\tdsra32 $4,$4,0x10\n\tlui $3,0x7000\n\tsw $4," #off "($3)" :: "r"(cval) : "$3", "$4")
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
#define SP_ADDR(h, l) ({ register u32 r; __asm__ volatile("lui %0," #h "\n\taddiu %0,%0," #l : "=r"(r)); r; })

void func_002B9F10(void)
{
    u32 SP_rv2;
    u32 SP_rv1;
    SP_SW0(0x1158);
    SP_SW_W16(0x1150, SP_LH(0x1118, 0xA4));
    if (SP_LW(0x1150)) {
        SP_rv2 = func_002B9E50();
    } else {
        SP_rv1 = func_002B9E20();
    }
}

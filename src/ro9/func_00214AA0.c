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
#define SP_LBU(ch, k) ({ register u32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tlbu $2," #k "($2)" : "=r"(r)); r; })
#define SP_LH16(ch, k) ({ register u32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tlhu $2," #k "($2)" : "=r"(r)); r; })
#define SP_LH(ch, k) ({ register s32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tlh $2," #k "($2)" : "=r"(r)); r; })
#define SP_SB0(ch, k) __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tsb $0," #k "($2)" : : : "$2")
#define SP_SB(ch, k, v) __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tsb %0," #k "($2)" :: "r"(v) : "$2")
#define SP_SH(ch, k, v) __asm__ volatile("lui $2,0x7000\n\tlw $2," #ch "($2)\n\tsh %0," #k "($2)" :: "r"(v) : "$2")
#define SP_SW(off, v) __asm__ volatile("lui $2,0x7000\n\tsw %0," #off "($2)" :: "r"(v) : "$2")
#define SP_SW_W8(off, cval) __asm__ volatile("dsll32 $5,%0,0x18\n\tdsra32 $5,$5,0x18\n\tlui $2,0x7000\n\tsw $5," #off "($2)" :: "r"(cval) : "$2", "$5")
#define SP_SW_W16(off, cval) __asm__ volatile("dsll32 $5,%0,0x10\n\tdsra32 $5,$5,0x10\n\tlui $2,0x7000\n\tsw $5," #off "($2)" :: "r"(cval) : "$2", "$5")
#define SP_W8TO(out, v) __asm__ volatile("dsll32 %0,%1,0x18\n\tdsra32 %0,%0,0x18" : "=r"(out) : "r"(v))
#define SP_W16TO(out, v) __asm__ volatile("dsll32 %0,%1,0x10\n\tdsra32 %0,%0,0x10" : "=r"(out) : "r"(v))
#define SP_ANDI(v, m) ({ register u32 r; __asm__ volatile("andi %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_ORI(v, m) ({ register u32 r; __asm__ volatile("ori %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_XORI(v, m) ({ register u32 r; __asm__ volatile("xori %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_ADDIU(v, m) ({ register u32 r; __asm__ volatile("addiu %0,%1," #m : "=r"(r) : "r"(v)); r; })
#define SP_SLL(v, s) ({ register u32 r; __asm__ volatile("sll %0,%1," #s : "=r"(r) : "r"(v)); r; })
#define SP_SRA(v, s) ({ register u32 r; __asm__ volatile("sra %0,%1," #s : "=r"(r) : "r"(v)); r; })
#define SP_ADDR(h, l) ({ register u32 r; __asm__ volatile("lui %0," #h "\n\taddiu %0,%0," #l : "=r"(r)); r; })

void func_00214AA0(void)
{
    register u32 SP_a1 asm("$5");
    register u32 SP_a2 asm("$6");
    register u32 SP_a0 asm("$4");
    u32 SP_w1;
    u32 SP_rv2;
    u32 SP_rv3;
    SP_W8TO(SP_w1, SP_LB(0x1118, 0x2));
    SP_a1 = SP_ANDI(SP_w1, 0xFFFF);
    SP_a2 = SP_ANDI(SP_ANDI(SP_LB(0x1118, 0x3), 0xFF), 0xFF);
    SP_a0 = SP_ADDR(0x5B, 0x610);
    SP_rv2 = func_00119E20(SP_a0, SP_a1, SP_a2);
    SP_rv3 = func_005819E0(SP_a0, SP_a1, SP_a2);
}

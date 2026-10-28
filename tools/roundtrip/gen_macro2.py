#!/usr/bin/env python3
"""Macro-mode generator for widen-family functions (ee-gcc 2.96).  v3.

v3: parametrized chain register ($2/$3 candidates per function), pure-asm
widen macros (SP_W8TO), SP_ADDR lui+addiu constants, register-asm-var
pinned call arguments (a0-a3), decode-first structuring (nested if/else
allowed), call return values via extern-u32 + temp.
"""
import glob
import os
import re
import subprocess
import sys
from collections import Counter

sys.path.insert(0, "/home/user/sfzfg/roundtrip/pilots")
import gen_c_family4 as G

ROOT = G.ROOT

MACROS_T = r'''typedef unsigned int u32;
typedef unsigned short u16;
typedef signed char s8;
typedef signed int s32;
#define SP_SW0(off) __asm__ volatile("lui {B},0x7000\n\tsw $0," #off "({B})" : : : "{B}")
#define SP_SW0_R2(off) __asm__ volatile("lui $2,0x7000\n\tsw $0," #off "($2)" : : : "$2")
#define SP_SW0_R3(off) __asm__ volatile("lui $3,0x7000\n\tsw $0," #off "($3)" : : : "$3")
#define SP_SW_R2(off, v) __asm__ volatile("lui $2,0x7000\n\tsw %0," #off "($2)" :: "r"(v) : "$2")
#define SP_SW_R3(off, v) __asm__ volatile("lui $3,0x7000\n\tsw %0," #off "($3)" :: "r"(v) : "$3")
#define SP_SB_R2(off, v) __asm__ volatile("lui $2,0x7000\n\tsb %0," #off "($2)" :: "r"(v) : "$2")
#define SP_SB_R3(off, v) __asm__ volatile("lui $3,0x7000\n\tsb %0," #off "($3)" :: "r"(v) : "$3")
#define SP_SH_R2(off, v) __asm__ volatile("lui $2,0x7000\n\tsh %0," #off "($2)" :: "r"(v) : "$2")
#define SP_SH_R3(off, v) __asm__ volatile("lui $3,0x7000\n\tsh %0," #off "($3)" :: "r"(v) : "$3")
#define SP_LW(off) ({ register u32 r asm("{D}"); __asm__ volatile("lui {B},0x7000\n\tlw {B}," #off "({B})" : "=r"(r)); r; })
#define SP_LW0_R2(off) ({ register u32 r asm("$2"); __asm__ volatile("lui {B},0x7000\n\tlw $2," #off "({B})" : "=r"(r)); r; })
#define SP_LW0_R3(off) ({ register u32 r asm("$3"); __asm__ volatile("lui {B},0x7000\n\tlw $3," #off "({B})" : "=r"(r)); r; })
#define SP_LW_R3(off) ({ register u32 r asm("$3"); __asm__ volatile("lui $3,0x7000\n\tlw $3," #off "($3)" : "=r"(r)); r; })
#define SP_LW_R2(off) ({ register u32 r asm("$2"); __asm__ volatile("lui $2,0x7000\n\tlw $2," #off "($2)" : "=r"(r)); r; })
#define SP_LB(ch, k) ({ register s8 r asm("{D}"); __asm__ volatile("lui {B},0x7000\n\tlw {B}," #ch "({B})\n\tlb {D}," #k "({B})" : "=r"(r)); r; })
#define SP_LB0(k) ({ register s8 r asm("{D}"); __asm__ volatile("lui {B},0x7000\n\tlb {D}," #k "({B})" : "=r"(r)); r; })
#define SP_LB0_R2(k) ({ register s8 r asm("$2"); __asm__ volatile("lui {B},0x7000\n\tlb $2," #k "({B})" : "=r"(r)); r; })
#define SP_LB0_R3(k) ({ register s8 r asm("$3"); __asm__ volatile("lui {B},0x7000\n\tlb $3," #k "({B})" : "=r"(r)); r; })
#define SP_LH0(k) ({ register s32 r asm("{D}"); __asm__ volatile("lui {B},0x7000\n\tlh {D}," #k "({B})" : "=r"(r)); r; })
#define SP_LH0_R2(k) ({ register s32 r asm("$2"); __asm__ volatile("lui {B},0x7000\n\tlh $2," #k "({B})" : "=r"(r)); r; })
#define SP_LH0_R3(k) ({ register s32 r asm("$3"); __asm__ volatile("lui {B},0x7000\n\tlh $3," #k "({B})" : "=r"(r)); r; })
#define SP_LHU0(k) ({ register u32 r asm("{D}"); __asm__ volatile("lui {B},0x7000\n\tlhu {D}," #k "({B})" : "=r"(r)); r; })
#define SP_LHU0_R2(k) ({ register u32 r asm("$2"); __asm__ volatile("lui {B},0x7000\n\tlhu $2," #k "({B})" : "=r"(r)); r; })
#define SP_LHU0_R3(k) ({ register u32 r asm("$3"); __asm__ volatile("lui {B},0x7000\n\tlhu $3," #k "({B})" : "=r"(r)); r; })
#define SP_LBU0(k) ({ register u32 r asm("{D}"); __asm__ volatile("lui {B},0x7000\n\tlbu {D}," #k "({B})" : "=r"(r)); r; })
#define SP_LBU0_R2(k) ({ register u32 r asm("$2"); __asm__ volatile("lui {B},0x7000\n\tlbu $2," #k "({B})" : "=r"(r)); r; })
#define SP_LBU0_R3(k) ({ register u32 r asm("$3"); __asm__ volatile("lui {B},0x7000\n\tlbu $3," #k "({B})" : "=r"(r)); r; })
#define SP_LBU(ch, k) ({ register u32 r asm("{D}"); __asm__ volatile("lui {B},0x7000\n\tlw {B}," #ch "({B})\n\tlbu {D}," #k "({B})" : "=r"(r)); r; })
#define SP_LH16(ch, k) ({ register u32 r asm("{D}"); __asm__ volatile("lui {B},0x7000\n\tlw {B}," #ch "({B})\n\tlhu {D}," #k "({B})" : "=r"(r)); r; })
#define SP_LH(ch, k) ({ register s32 r asm("{D}"); __asm__ volatile("lui {B},0x7000\n\tlw {B}," #ch "({B})\n\tlh {D}," #k "({B})" : "=r"(r)); r; })
#define SP_SB0(ch, k) __asm__ volatile("lui {B},0x7000\n\tlw {B}," #ch "({B})\n\tsb $0," #k "({B})" : : : "{B}")
#define SP_SB(ch, k, v) __asm__ volatile("lui {B},0x7000\n\tlw {B}," #ch "({B})\n\tsb %0," #k "({B})" :: "r"(v) : "{B}")
#define SP_SH(ch, k, v) __asm__ volatile("lui {B},0x7000\n\tlw {B}," #ch "({B})\n\tsh %0," #k "({B})" :: "r"(v) : "{B}")
#define SP_SW(off, v) __asm__ volatile("lui {B},0x7000\n\tsw %0," #off "({B})" :: "r"(v) : "{B}")
#define SP_SW_W8(off, cval) __asm__ volatile("dsll32 {S},%0,0x18\n\tdsra32 {S},{S},0x18\n\tlui {B},0x7000\n\tsw {S}," #off "({B})" :: "r"(cval) : "{B}", "{S}")
#define SP_SW_W16(off, cval) __asm__ volatile("dsll32 {S},%0,0x10\n\tdsra32 {S},{S},0x10\n\tlui {B},0x7000\n\tsw {S}," #off "({B})" :: "r"(cval) : "{B}", "{S}")
#define SP_SW_W8_R2(off, cval) __asm__ volatile("dsll32 $2,%0,0x18\n\tdsra32 $2,$2,0x18\n\tlui {B},0x7000\n\tsw $2," #off "({B})" :: "r"(cval) : "{B}", "$2")
#define SP_SW_W8_R3(off, cval) __asm__ volatile("dsll32 $3,%0,0x18\n\tdsra32 $3,$3,0x18\n\tlui {B},0x7000\n\tsw $3," #off "({B})" :: "r"(cval) : "{B}", "$3")
#define SP_SW_W8_R4(off, cval) __asm__ volatile("dsll32 $4,%0,0x18\n\tdsra32 $4,$4,0x18\n\tlui {B},0x7000\n\tsw $4," #off "({B})" :: "r"(cval) : "{B}", "$4")
#define SP_SW_W8_R5(off, cval) __asm__ volatile("dsll32 $5,%0,0x18\n\tdsra32 $5,$5,0x18\n\tlui {B},0x7000\n\tsw $5," #off "({B})" :: "r"(cval) : "{B}", "$5")
#define SP_SW_W8_R6(off, cval) __asm__ volatile("dsll32 $6,%0,0x18\n\tdsra32 $6,$6,0x18\n\tlui {B},0x7000\n\tsw $6," #off "({B})" :: "r"(cval) : "{B}", "$6")
#define SP_SW_W16_R2(off, cval) __asm__ volatile("dsll32 $2,%0,0x10\n\tdsra32 $2,$2,0x10\n\tlui {B},0x7000\n\tsw $2," #off "({B})" :: "r"(cval) : "{B}", "$2")
#define SP_SW_W16_R3(off, cval) __asm__ volatile("dsll32 $3,%0,0x10\n\tdsra32 $3,$3,0x10\n\tlui {B},0x7000\n\tsw $3," #off "({B})" :: "r"(cval) : "{B}", "$3")
#define SP_SW_W16_R4(off, cval) __asm__ volatile("dsll32 $4,%0,0x10\n\tdsra32 $4,$4,0x10\n\tlui {B},0x7000\n\tsw $4," #off "({B})" :: "r"(cval) : "{B}", "$4")
#define SP_SW_W16_R5(off, cval) __asm__ volatile("dsll32 $5,%0,0x10\n\tdsra32 $5,$5,0x10\n\tlui {B},0x7000\n\tsw $5," #off "({B})" :: "r"(cval) : "{B}", "$5")
#define SP_SW_W16_R6(off, cval) __asm__ volatile("dsll32 $6,%0,0x10\n\tdsra32 $6,$6,0x10\n\tlui {B},0x7000\n\tsw $6," #off "({B})" :: "r"(cval) : "{B}", "$6")
#define SP_SB_D(off, v) __asm__ volatile("lui {B},0x7000
	sb %0," #off "({B})" :: "r"(v) : "{B}")
#define SP_SH_D(off, v) __asm__ volatile("lui {B},0x7000
	sh %0," #off "({B})" :: "r"(v) : "{B}")
#define SP_SW_D(off, v) __asm__ volatile("lui {B},0x7000
	sw %0," #off "({B})" :: "r"(v) : "{B}")
#define SP_LBW(ch, k) ({ register s32 r asm("{D}"); __asm__ volatile("lui {B},0x7000
	lw {B}," #ch "({B})
	lb {D}," #k "({B})
	dsll32 {D},{D},0x18
	dsra32 {D},{D},0x18" : "=r"(r)); r; })
#define SP_LHW(ch, k) ({ register s32 r asm("{D}"); __asm__ volatile("lui {B},0x7000
	lw {B}," #ch "({B})
	lh {D}," #k "({B})
	dsll32 {D},{D},0x10
	dsra32 {D},{D},0x10" : "=r"(r)); r; })
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
'''

REJECT = {}
LW_RE = re.compile(r"^SP_LW(?:(?:_R[23])?(?:0_R[23])?0?|_B\dD\d)\(0x([0-9A-F]+)\)$")
ATOM_PTR_RE = re.compile(r"^SP_([ra]\d+)$")
ABS_RE = re.compile(r"^\*\(volatile u32 \*\)0x([0-9A-F]+)$")
ARG_REGS = {4: "SP_a0", 5: "SP_a1", 6: "SP_a2", 7: "SP_a3"}


def gp_macro_def(kind, p, h, v):
    """Dynamic through-pointer macro: lui $H,hi; lw $P,lo($H); OP $V,off($P).
    kind: lw/lb/lbu/lh/lhu | lbw/lhw (widen-fused in-place on V)."""
    ops = {"lw": ("u32", "lw"), "lb": ("s32", "lb"), "lbu": ("u32", "lbu"),
           "lh": ("s32", "lh"), "lhu": ("u32", "lhu")}
    if kind in ("lbw", "lhw"):
        ct, op = "s32", "lb" if kind == "lbw" else "lh"
        sh = "0x18" if kind == "lbw" else "0x10"
        tail = f"\\n\\tdsll32 ${v},${v},{sh}\\n\\tdsra32 ${v},${v},{sh}"
        name = f"SP_{kind.upper()}_G{p}_{h}_{v}"
    else:
        ct, op = ops[kind]
        tail = ""
        name = f"SP_{op.upper()}_G{p}_{h}_{v}"
    define = (f"#define {name}(hi, lo, off) ({{ register {ct} r asm(\"${v}\"); "
              f"__asm__ volatile(\"lui ${h},\" #hi \"\\n\\tlw ${p},\" #lo \"(${h})"
              f"\\n\\t{op} ${v},\" #off \"(${p}){tail}\" : \"=r\"(r)); r; }})")
    return name, define


def abs_fused_macro_def(kind, B, D, W, hi, off):
    """ABS-global signed load with the widen pair fused in-place on W:
    lui $B,hi; lb/lh $D,off($B); dsll32 $W,$D,sh; dsra32 $W,$W,sh."""
    op = "lb" if kind == "lb" else "lh"
    sh = "0x18" if kind == "lb" else "0x10"
    name = f"SP_{kind.upper()}W_A{B}_{D}_{W}_{hi:X}_{off & 0xFFFF:X}"
    define = (f"#define {name} ({{ register s32 r asm(\"${W}\"); "
              f"__asm__ volatile(\"lui ${B},0x{hi:X}\\n\\t{op} ${D},{foff(off)}(${B})"
              f"\\n\\tdsll32 ${W},${D},{sh}\\n\\tdsra32 ${W},${W},{sh}\" "
              f": \"=r\"(r) : : \"{B}\", \"{D}\"); r; }})")
    return name, define


def hi_addu_macro_def(D, H, hi_first):
    """Pinned pointer + lui-constant add (Addendum 28): the original does
    `lui $H,hv; addu $D,$X,$H` (constant in its own register, addu —
    NOT daddu, NOT $at).  hi_first: the hi operand's position in the
    insn (t[1] vs t[2]).  Args: (hv, v)."""
    if hi_first:
        tpl = "addu %0,%1,%2"   # %1=_h, %2=v
        args = '"r"(_h), "r"(v)'
    else:
        tpl = "addu %0,%1,%2"   # %1=v, %2=_h
        args = '"r"(v), "r"(_h)'
    name = f"SP_ADDLUI_T{D}_{H}{'F' if hi_first else ''}"
    define = (f"#define {name}(hv, v) ({{ register u32 _h asm(\"${H}\"); "
              f"register u32 r asm(\"${D}\"); "
              f"__asm__ volatile(\"\" : \"=r\"(r) : \"r\"(v)); "
              f"__asm__ volatile(\"lui %0,%1\" : \"=r\"(_h) : \"n\"(hv)); "
              f"__asm__ volatile(\"{tpl}\" : \"=r\"(r) : {args}); r; }})")
    return name, define


def hi_op_macro_def(op, D, H):
    """Pinned hi-materialize + op pair (Addendum 25): the original does
    `lui $H,hv; op $D,$H,imm` — materializing the constant into its OWN
    pinned register keeps gcc from folding it into the destination."""
    name = f"SP_{op.upper()}HI_T{D}_{H}"
    define = (f"#define {name}(hv, i) ({{ register u32 _h asm(\"${H}\"); "
              f"register u32 r asm(\"${D}\"); "
              f"__asm__ volatile(\"lui %0,%1\" : \"=r\"(_h) : \"n\"(hv)); "
              f"__asm__ volatile(\"{op} %0,%1,%2\" : \"=r\"(r) "
              f": \"r\"(_h), \"n\"(i)); r; }})")
    return name, define


def abs_ws_macro_def(kind, B, S):
    """ABS-global WIDEN-store with SEPARATE base and scratch registers
    (the old single-register variants clobbered the widened value with
    the base lui).  kind: w8/w16.  Args: (hi, lo, cval)."""
    sh = "0x18" if kind == "w8" else "0x10"
    name = f"SP_{kind.upper()}_ABS_B{B}_S{S}"
    define = (f"#define {name}(hi, lo, cval) __asm__ volatile("
              f"\"dsll32 ${S},%0,{sh}\\n\\tdsra32 ${S},${S},{sh}"
              f"\\n\\tlui ${B},\" #hi \"\\n\\tsw ${S},\" #lo \"(${B})\" "
              f":: \"r\"(cval) : \"${B}\", \"${S}\")")
    return name, define


def chain2_macro_def(kind, B, D, W=None):
    """Two-level scratchpad access with ALL registers per-site:
    `lui $B,0x7000; lw $B,ch($B); OP $D,k($B)` — optionally widen-fused
    (kind lbw/lhw: pair in-place on $W, read from $D) or store-fused
    (kind lbsb/shsb: `lb $D,k1($B); sb $D,k2($B)`)."""
    types = {"lb": ("s32", "lb"), "lbu": ("u32", "lbu"), "lh": ("s32", "lh"),
             "lhu": ("u32", "lhu"), "lw": ("u32", "lw")}
    clob = ", ".join('"%s"' % r for r in ({B, D, W} if W else {B, D}))
    if kind in ("lbw", "lhw"):
        op = "lb" if kind == "lbw" else "lh"
        sh = "0x18" if kind == "lbw" else "0x10"
        name = f"SP_{kind.upper()}_T{B}_{D}_{W}"
        define = (f"#define {name}(ch, k) ({{ register s32 r asm(\"${W}\"); "
                  f"__asm__ volatile(\"lui ${B},0x7000\\n\\tlw ${B},\" #ch \"(${B})"
                  f"\\n\\t{op} ${D},\" #k \"(${B})\\n\\tdsll32 ${W},${D},{sh}"
                  f"\\n\\tdsra32 ${W},${W},{sh}\" : \"=r\"(r) : : {clob}); r; }})")
    elif kind in ("lbsb", "shsb"):
        op = "lb" if kind == "lbsb" else "lh"
        st = "sb" if kind == "lbsb" else "sh"
        name = f"SP_{kind.upper()}_T{B}_{D}"
        define = (f"#define {name}(ch, k1, k2) __asm__ volatile("
                  f"\"lui ${B},0x7000\\n\\tlw ${B},\" #ch \"(${B})"
                  f"\\n\\t{op} ${D},\" #k1 \"(${B})\\n\\t{st} ${D},\" #k2 \"(${B})\" "
                  f":: : {clob}, \"memory\")")
    else:
        ct, op = types[kind]
        name = f"SP_{op.upper()}_T{B}_{D}"
        define = (f"#define {name}(ch, k) ({{ register {ct} r asm(\"${D}\"); "
                  f"__asm__ volatile(\"lui ${B},0x7000\\n\\tlw ${B},\" #ch \"(${B})"
                  f"\\n\\t{op} ${D},\" #k \"(${B})\" : \"=r\"(r) : : \"{B}\"); r; }})")
    return name, define


def alu_t_macro_def(op, D, two=False):
    """Destination-pinned ALU op (Addendum 19): the result register comes
    from the ORIGINAL's insn, so gcc cannot choose (input values are
    themselves pinned asm-vars, so no copies are needed)."""
    if two:
        name = f"SP_{op.upper()}2_T{D}"
        define = (f"#define {name}(a, b) ({{ register u32 r asm(\"${D}\"); "
                  f"__asm__ volatile(\"{op} %0,%1,%2\" : \"=r\"(r) "
                  f": \"r\"(a), \"r\"(b)); r; }})")
    else:
        name = f"SP_{op.upper()}I_T{D}"
        define = (f"#define {name}(a, i) ({{ register u32 r asm(\"${D}\"); "
                  f"__asm__ volatile(\"{op} %0,%1,%2\" : \"=r\"(r) "
                  f": \"r\"(a), \"n\"(i)); r; }})")
    return name, define


def li_t_macro_def(D):
    """Destination-pinned constant materialization: addiu $D,$zero,imm."""
    name = f"SP_LI_T{D}"
    define = (f"#define {name}(i) ({{ register u32 r asm(\"${D}\"); "
              f"__asm__ volatile(\"addiu %0,$0,%1\" : \"=r\"(r) "
              f": \"n\"(i)); r; }})")
    return name, define


def addr_t_macro_def(D):
    """Destination-pinned lui+addiu address materialization."""
    name = f"SP_ADDR_T{D}"
    define = (f"#define {name}(h, l) ({{ register u32 r asm(\"${D}\"); "
              f"__asm__ volatile(\"lui %0,%1\\n\\taddiu %0,%0,%2\" "
              f": \"=r\"(r) : \"n\"(h), \"n\"(l)); r; }})")
    return name, define


def lui_t_macro_def(D):
    """Destination-pinned bare-lui constant materialization (Addendum 30):
    anchors an arg-home hi constant at the original lui's position."""
    name = f"SP_LUI_T{D}"
    define = (f"#define {name}(h) ({{ register u32 r asm(\"${D}\"); "
              f"__asm__ volatile(\"lui %0,%1\" : \"=r\"(r) : \"n\"(h)); r; }})")
    return name, define


def zstore_macro_def(op, B):
    """Zero store to the scratchpad at the ORIGINAL's width (Addendum 30):
    sb/sh zero stores were rendered as word SP_SW0 — wrong opcode."""
    name = f"SP_{op.upper()}0_R{B}"
    define = ('#define %s(off) __asm__ volatile("lui $%d,0x7000\\n\\t'
              '%s $0," #off "($%d)" : : : "$%d")' % (name, B, op, B, B))
    return name, define


def zptr_store_macro_def(op, P):
    """Zero store THROUGH A LOADED POINTER (Addendum 30): the store
    operand is hardwired to $0 — passing a literal 0 through the "r"
    constraint made gcc materialize it in a temp first (or $v0,$zero)."""
    name = f"SP_{op.upper()}0_P{P}"
    define = ('#define %s(pexp, off) ({ register u32 _p asm("$%d") = '
              '(u32)(pexp); __asm__ volatile("%s $0," #off "($%d)" '
              ': : : "memory"); })' % (name, P, op, P))
    return name, define


def cd_load_macro_def(op, B, D):
    """Chain-direct load with BOTH registers per-site (Addendum 24):
    lui $B,0x7000; OP $D,off($B).  op: LW/LB/LBU/LH/LHU."""
    ct = "s32" if op in ("LB", "LH") else "u32"
    name = f"SP_{op}_B{B}D{D}"
    define = (f"#define {name}(off) ({{ register {ct} r asm(\"${D}\"); "
              f"__asm__ volatile(\"lui ${B},0x7000\\n\\t{op.lower()} ${D},\" "
              f"#off \"(${B})\" : \"=r\"(r)); r; }})")
    return name, define


def cw_load_macro_def(op, B, D, W, sh):
    """One-level chain-direct load + widen pair fused (Addendum 37):
    `lui $B,0x7000; op $D,off($B); dsll32 $W,$D,sh; dsra32 $W,$W,sh` —
    the load hits the ORIGINAL's load-dst $D first; the widen pair goes
    to ITS dst $W (split when the original used two registers)."""
    name = f"SP_{op.upper()}W0_B{B}D{D}W{W}"
    if D == W:
        define = ('#define %s(off) ({ register s32 r asm("$%d"); '
                  '__asm__ volatile("lui $%d,0x7000\\n\\t%s %%0,%s($%d)'
                  '\\n\\tdsll32 %%0,%%0,%s\\n\\tdsra32 %%0,%%0,%s" '
                  ': "=r"(r) : : "$%d"); r; })'
                  % (name, W, B, op, '" #off "', B, sh, sh, B))
    else:
        define = ('#define %s(off) ({ register s32 r asm("$%d"); '
                  '__asm__ volatile("lui $%d,0x7000\\n\\t%s $%d,%s($%d)'
                  '\\n\\tdsll32 $%d,$%d,%s\\n\\tdsra32 $%d,$%d,%s" '
                  ': "=r"(r) : : "$%d","$%d"); r; })'
                  % (name, W, B, op, D, '" #off "', B,
                     W, D, sh, W, W, sh, B, D))
    return name, define


def atom_load_macro_def(op, P, D):
    """Load THROUGH a tied atom pointer (Addendum 32): the pointer register
    is baked in (SP_rP / arg_aP); the load is tied at its own position —
    used when the pointer load is NOT adjacent, where a fused chain2
    macro would re-materialize the pointer far from the original's load."""
    name = f"SP_{op.upper()}_A{P}D{D}"
    t = "s32" if op in ("lb", "lh") else "u32"
    pn = ARG_REGS[P] if P in ARG_REGS else f"SP_r{P}"
    define = ('#define %s(off) ({ register %s r asm("$%d"); '
              '__asm__ volatile("%s %%0,%%1($%d)" : "=r"(r) : "i"(off), '
              '"r"(%s)); r; })' % (name, t, D, op, P, pn))
    return name, define


def atom_load_add_macro_def(op, P, D):
    """Pointer ARITHMETIC then load (Addendum 38): the original does
    `addiu $P,$P,K; op $D,off($P)` in place on the tied atom's register —
    both insns in one macro (an un-emitted ALU step plus the load)."""
    name = f"SP_{op.upper()}AI{P}D{D}"
    pn = ARG_REGS[P] if P in ARG_REGS else f"SP_r{P}"
    define = ('#define %s(k, off) ({ register u32 r asm("$%d"); '
              '__asm__ volatile("addiu $%d,$%d," #k "\\n\\t%s %%0," #off '
              '"($%d)" : "=r"(r) : : "$%d"); r; })'
              % (name, D, P, P, op, P, P))
    return name, define


def ptr_store_macro(op, p, v, h=None):
    """Store through a pointer VALUE: materialize pexp into $p, store.
    op: sw/sb/sh.  v (optional) = the value's pinned register: the value
    is initialized BEFORE the pointer (insn order — gcc evaluation-order
    freedom killed by statement order)."""
    if v:
        name = f"SP_{op.upper()}_P{p}V{v}"
        define = (f"#define {name}(pexp, off, val) ({{ "
                  f"register u32 _v asm(\"${v}\") = (u32)(val); "
                  f"register u32 _p asm(\"${p}\") = (u32)(pexp); "
                  f"__asm__ volatile(\"{op} %0,\" #off \"(${p})\" "
                  f":: \"r\"(_v) : \"memory\"); }})")
    else:
        name = f"SP_{op.upper()}_P{p}"
        define = (f"#define {name}(pexp, off, val) ({{ register u32 _p asm(\"${p}\") = (u32)(pexp); "
                  f"__asm__ volatile(\"{op} %0,\" #off \"(${p})\" :: \"r\"(val) : \"memory\"); }})")
    return name, define


def rmw_macro(op, p, h, v):
    """Read-modify-write through an abs-global pointer, one macro:
    lui $H,hi; lw $P,lo($H); LOAD $V,off($P); addiu $V,$V,imm; op $V,off($P).
    op = the STORE mnemonic (sb/sh); the load is its read counterpart.
    Returns (name, define); the statement-expression value is the modified
    value, so the env can chain it."""
    load = {"sb": "lb", "sh": "lh"}[op]
    name = f"SP_RMW{op.upper()}_G{p}_{h}_{v}"
    define = (f"#define {name}(hi, lo, off, imm) ({{ register u32 _p asm(\"${p}\"); "
              f"register s32 _v asm(\"${v}\"); "
              f"__asm__ volatile(\"lui ${h},\" #hi \"\\n\\tlw ${p},\" #lo \"(${h})"
              f"\\n\\t{load} ${v},\" #off \"(${p})\\n\\taddiu ${v},${v},\" #imm "
              f"\"\\n\\t{op} ${v},\" #off \"(${p})\" : \"=&r\"(_v), \"=&r\"(_p)); _v; }})")
    return name, define


def foff(x):
    if x < 0:
        return "-0x%X" % -x
    if x >= 0x8000:
        return "-0x%X" % (0x10000 - x)
    return "0x%X" % x


def macros_for(base, data=None, widen=None):
    txt = MACROS_T.replace("{B}", base).replace("{D}", data or base)
    if widen is None:
        widen = "$4" if (data or base) != "$4" else "$5"
    return txt.replace("{S}", widen)


class Ctx:
    def __init__(self, base):
        self.base = base
        self.decls = []
        self.used_args = set()
        self.params = []        # incoming a0-a3, in order
        self.nc = [0]
        self.xj = 0             # cross-jump shared-else label counter
        self.xjlbl = {}         # inverted-if join address -> label (owner)
        self.xjn = 0            # fresh label counter
        self.gp = []            # dynamically emitted #define lines
        self.gp_seen = set()
        self.temp_map = {}      # expr text -> materialized temp name
        self.tn = 0

    def gp_def(self, name, line):
        if name not in self.gp_seen:
            self.gp_seen.add(name)
            self.gp.append(line)


CTX = None


def macro_decode_run(insns, env=None, nc=None):
    ctx = CTX
    if env is None:
        env = {}
    acts = []
    n = len(insns)

    def emit(t):
        acts.append(("mstmt", t))

    def declare_arg(rn):
        if rn not in ctx.used_args:
            ctx.used_args.add(rn)
            ctx.decls.append("    register u32 %s asm(\"$%d\");" % (ARG_REGS[rn], rn))

    def param_of(rn):
        """Treat a cold a0-a3 as an incoming parameter (K&R signature)."""
        if rn not in ctx.params:
            ctx.params.append(rn)
        return "arg_a%d" % (rn - 4)

    def tie_at(dst, calltext):
        """Materialize a pinned macro call AT ITS DECODED POSITION as an
        empty-volatile tie (Addendum 29).  Ties execute in program order, so
        a value the original produced here can no longer float into a later
        statement's argument evaluation (pinnify hoists at the consumer,
        which permutes order when two values feed one store).  The atom
        name matches pinnify's convention so decls dedupe."""
        if dst in ARG_REGS:
            declare_arg(dst)
            emit("__asm__ volatile(\"\" : \"=r\"(%s) : \"0\"(%s));"
                 % (ARG_REGS[dst], calltext))
            return ARG_REGS[dst]
        atom = f"SP_r{dst}"
        acts.append(("mdecl", f"register u32 {atom} asm(\"${dst}\");"))
        emit(f"__asm__ volatile(\"\" : \"=r\"({atom}) : \"0\"({calltext}));")
        return atom

    def setreg(dst, entry):
        # Addendum 29: a bound T-macro expression is materialized AT THIS
        # POSITION as a tie — the original produced the value here, and
        # deferred evaluation lets gcc permute independent statements.
        # Already-tied atoms pass through untouched.
        E = entry[2]
        if entry[1] == "u32" and isinstance(E, str) and \
                E.startswith("SP_") and "(" in E and E.endswith(")") and \
                not re.match(r"^SP_r\d+$", E):
            E = tie_at(dst, E)
            entry = ("val", "u32", E, None)
        if dst in ARG_REGS:
            declare_arg(dst)
            kind, E = entry[1], entry[2]
            if E != ARG_REGS[dst]:          # tied atoms are already placed
                if kind == "wraw":
                    emit("%s(%s, %s);"
                         % ("SP_W8TO" if entry[3] == "w8" else "SP_W16TO",
                            ARG_REGS[dst], E))
                else:
                    emit("%s = %s;" % (ARG_REGS[dst], E))
            env[dst] = ("val", "u32", ARG_REGS[dst], None)
        else:
            env[dst] = entry

    def wpair(dstreg, srcreg, sh_text):
        e = env.get(srcreg)
        if e is None:
            raise G.Stop("widen-orphan")
        kind = {"0x18": "w8", "24": "w8", "0x10": "w16", "16": "w16"}.get(sh_text)
        if not kind:
            raise G.Stop("widen-sh")
        if e[1] == "wraw":
            setreg(dstreg, e)
            return
        if e[1] not in ("s32", "s8", "u32"):
            # u32 allowed (Addendum 18): the pair is explicit asm, so it is
            # byte-exact by construction whatever the C type of the source
            raise G.Stop("widen-src:" + e[1])
        wto = "SP_W8TO" if kind == "w8" else "SP_W16TO"
        if dstreg in ARG_REGS:
            declare_arg(dstreg)
            emit(f"{wto}({ARG_REGS[dstreg]}, {e[2]});")
            env[dstreg] = ("val", "u32", ARG_REGS[dstreg], None)
            return
        if dstreg in (2, 3, 5, 6):
            # Pinned widen-out (Addendum 29): the original's pair dst is
            # visible; a free temp lets gcc pick (it stacked both pairs of
            # a double widen into one reg — 00280800 class).  Same atom
            # naming as pinnify so decls dedupe.
            atom = f"SP_r{dstreg}"
            acts.append(("mdecl", f"register u32 {atom} asm(\"${dstreg}\");"))
            emit(f"{wto}({atom}, {e[2]});")
            env[dstreg] = ("val", "u32", atom, None)
            return
        nc[0] += 1
        tv = f"SP_w{nc[0]}"
        acts.append(("mdecl", f"u32 {tv};"))
        emit(f"{wto}({tv}, {e[2]});")
        env[dstreg] = ("val", "u32", tv, None)

    k = 0
    while k < n:
        i = insns[k]
        m = i.mnemonic
        t = G.toks_of(i)

        if m in ("nop", "jr") or m in G.MMI:
            k += 1
            continue
        if m == "ext" and len(t) == 4 and t[3][0] == "i" and int(t[3][1], 0) == 1:
            k += 1
            continue
        if m in ("sd", "ld") and t and t[0][1] == "ra":
            k += 1
            continue

        if m == "lui":
            dst = G.rname(t[0][1])
            imm = int(t[1][1], 0)
            if imm == 0x7000:
                env[dst] = ("val", "chain", "SP", None)
            else:
                # Addendum 30/34: a PINNED-register hi constant is
                # materialized AT THE LUI'S POSITION (tied) — deferring
                # the fold to the consumer let gcc emit it after
                # intervening chains.  Skip when the NEXT insn consumes
                # it: the ADDR/hio/hi-addu macros re-materialize.
                if (dst in ARG_REGS or dst in (2, 3, 5, 6)) and k + 1 < n:
                    nt = G.toks_of(insns[k + 1])
                    if not (insns[k + 1].mnemonic in
                            ("addiu", "ori", "xori", "andi", "addu", "add")
                            and len(nt) >= 3 and G.rname(nt[1][1]) == dst):
                        nm, df = lui_t_macro_def(dst)
                        ctx.gp_def(nm, df)
                        tie_at(dst, f"{nm}(0x{imm:X})")
                # spare = this lui's own register (needed to pin the
                # constant materialization in hi-op pair macros)
                env[dst] = ("val", "hi", str(imm), dst)
            k += 1
            continue

        if m in ("lw", "lb", "lbu", "lhu", "lh"):
            dst = G.rname(t[0][1])
            off, basereg = t[1][1], G.rname(t[1][2])
            base = env.get(basereg)
            if base is None:
                raise G.Stop("load-cold")
            if base[1] == "chain":
                # Per-site chain register: the macro must use the SAME
                # register the ORIGINAL used as this load's base (a second
                # chain in $3 inside a $2-config function is common after a
                # call clobbers $v0).  Plain SP_LW is the config's own reg.
                if m == "lw":
                    opu = "LW"
                elif m in ("lb", "lbu", "lh", "lhu"):
                    opu = m.upper()
                else:
                    opu = None
                if opu:
                    # per-site BOTH registers (Addendum 24): base = the
                    # original's lui dst, value = the load's dst.
                    if basereg not in (2, 3, 4, 5, 6) or \
                            dst not in (2, 3, 4, 5, 6):
                        raise G.Stop(f"cd-reg:{basereg}/{dst}")
                    # Addendum 37: a widen pair on the load's dst fuses
                    # into a one-level load+widen macro tied here.
                    if m in ("lb", "lh") and k + 2 < n and \
                            insns[k + 1].mnemonic == "dsll32" and \
                            insns[k + 2].mnemonic == "dsra32":
                        sh = insns[k + 1].op_str.split(",")[-1].strip()
                        if sh in ("0x18", "24", "0x10", "16"):
                            W = G.rname(G.toks_of(insns[k + 1])[0][1])
                            if W not in (2, 3, 4, 5, 6):
                                raise G.Stop(f"cw-reg:{W}")
                            nm, df = cw_load_macro_def(m, basereg, dst, W, sh)
                            ctx.gp_def(nm, df)
                            watom = tie_at(W, f"{nm}({foff(off)})")
                            env[W] = ("val", "s32", watom, None)
                            if dst != W:
                                env.pop(dst, None)
                            k += 3
                            continue
                    nm, df = cd_load_macro_def(opu, basereg, dst)
                    ctx.gp_def(nm, df)
                    k2t = "s32" if m in ("lb", "lh") else "u32"
                    nxt = insns[k + 1] if k + 1 < n else None
                    nbase = G.rname(G.toks_of(nxt)[1][2]) \
                        if nxt is not None and \
                        nxt.mnemonic in ("lw", "lb", "lbu", "lh", "lhu") \
                        else None
                    if nbase == dst and dst == basereg:
                        # a through-load follows: keep the call TEXT so the
                        # u32 path fuses both levels into one chain2 macro
                        # at the follow-on's position (same insn sequence,
                        # so program order is preserved)
                        env[dst] = ("val", k2t, f"{nm}({foff(off)})", None)
                    else:
                        # Tied AT ITS POSITION (Addendum 29): the original's
                        # load runs in program order, not at its consumer.
                        atom = tie_at(dst, f"{nm}({foff(off)})")
                        # spare = (call text, load address): a follow-on
                        # load through this pointer re-parses the chain
                        # offset (LW_RE) and checks ADJACENCY before
                        # fusing a chain2 macro (Addendum 32)
                        env[dst] = ("val", k2t, atom,
                                    (f"{nm}({foff(off)})", i.address))
                else:
                    raise G.Stop("chain-direct:" + m)
            elif base[1] == "u32":
                # A TIED pointer (spare = (text, addr)) is already emitted
                # at its position — a fused chain2 macro would re-emit the
                # pointer load, so through-loads go via the 1-insn
                # atom-load (Addendum 32).  Fusion is for DEFERRED text
                # entries only (never separately emitted).
                spare = base[3]
                tied = isinstance(spare, tuple)
                ptext = (spare[0] if tied else (spare or base[2]))
                # Addendum 38: pointer ARITHMETIC — the base is a tied ATOM
                # (the addiu step on a pinned reg emitted its own tie, which
                # IS the original's addiu; this load goes through the atom)
                am = ATOM_PTR_RE.match(base[2] if isinstance(base[2], str)
                                       else "")
                if am and not tied:
                    P = (int(am.group(1)[1:]) if am.group(1)[0] == "r"
                         else 4 + int(am.group(1)[1:]))
                    if P in (2, 3, 4, 5, 6):
                        anm, adf = atom_load_macro_def(m, P, dst)
                        ctx.gp_def(anm, adf)
                        aatom = tie_at(dst, f"{anm}({foff(off)})")
                        k2t = "s32" if m in ("lb", "lh") else "u32"
                        env[dst] = ("val", k2t, aatom, None)
                        k += 1
                        continue
                mm = LW_RE.match(ptext)
                if not mm:
                    raise G.Stop("chain-computed")
                ch = int(mm.group(1), 16)
                k2t = "s32" if m in ("lb", "lh") else "u32"
                if tied:
                    anm, adf = atom_load_macro_def(m, basereg, dst)
                    ctx.gp_def(anm, adf)
                    aatom = tie_at(dst, f"{anm}({foff(off)})")
                    env[dst] = ("val", k2t, aatom, None)
                    k += 1
                    continue
                if m == "lw":
                    # Addendum 36: the fused [lui;lw] IS the original's
                    # insns at THIS position — tie it here; a value
                    # expression floats to its consumer and permutes order
                    atom = tie_at(dst, f"SP_LW({foff(off)})")
                    env[dst] = ("val", "u32", atom, None)
                elif m in ("lb", "lbu", "lh", "lhu"):
                    # Per-site two-level access (Addendum 16): B/D/W
                    # registers come from the ORIGINAL's insns, not the
                    # config.  Lookahead: widen pair -> lbw/lhw variant;
                    # same-pointer byte store -> fused lbsb/shsb.
                    B = basereg
                    D = dst
                    nxt = insns[k + 1] if k + 1 < n else None
                    st_t = G.toks_of(nxt) if nxt is not None else None
                    st_store = (nxt is not None and nxt.mnemonic in ("sb", "sh")
                                and st_t and G.rname(st_t[0][1]) == D
                                and G.rname(st_t[1][2]) == dst)
                    pair = None
                    if (k + 3 < n and insns[k + 2].mnemonic == "dsll32"
                            and insns[k + 3].mnemonic == "dsra32"):
                        pair = insns[k + 2].op_str.split(",")[-1].strip()
                    if pair in ("0x18", "24", "0x10", "16"):
                        W = G.rname(G.toks_of(insns[k + 2])[0][1])
                        if B not in (2, 3, 4, 5, 6) or D not in (2, 3, 4, 5, 6) \
                                or W not in (2, 3, 4, 5, 6):
                            raise G.Stop(f"chain2-reg:{B}/{D}/{W}")
                        kind = "lbw" if pair in ("0x18", "24") else "lhw"
                        nm, df = chain2_macro_def(kind, B, D, W)
                        ctx.gp_def(nm, df)
                        # Addendum 36: tied at the load's own position
                        watom = tie_at(W, f"{nm}(0x{ch:X}, {foff(off)})")
                        env[W] = ("val", "s32", watom, None)
                        if dst != W and dst != D:
                            env[dst] = ("val", "u32", base[2], None)
                        else:
                            env.pop(dst, None)
                        k += 4
                        continue
                    if st_store:
                        soff = st_t[1][1] if isinstance(st_t[1][1], int) \
                            else int(st_t[1][1], 0)
                        if B not in (2, 3, 4, 5, 6) or D not in (2, 3, 4, 5, 6):
                            raise G.Stop(f"chain2-reg:{B}/{D}")
                        kind = "lbsb" if nxt.mnemonic == "sb" else "shsb"
                        nm, df = chain2_macro_def(kind, B, D)
                        ctx.gp_def(nm, df)
                        emit(f"{nm}(0x{ch:X}, {foff(off)}, {foff(soff)});")
                        env.pop(dst, None)
                        env.pop(D, None)
                        k += 2
                        continue
                    if B not in (2, 3, 4, 5, 6) or D not in (2, 3, 4, 5, 6):
                        raise G.Stop(f"chain2-reg:{B}/{D}")
                    nm, df = chain2_macro_def(m, B, D)
                    ctx.gp_def(nm, df)
                    k2t = "s32" if m in ("lb", "lh") else "u32"
                    # Addendum 36: tied at the through-load's own position
                    catom = tie_at(D, f"{nm}(0x{ch:X}, {foff(off)})")
                    env[D] = ("val", k2t, catom, None)
                    # D == dst: the pointer register now holds the VALUE
                    # (already stored above — do NOT pop it).  D != dst:
                    # the pointer register survives untouched.
                else:
                    raise G.Stop("chain-computed")
            elif base[1] == "hi":
                addr = (int(base[2]) << 16) + off
                # GP fusion: a through-pointer access on the pointer this
                # abs load produces (`lui $H,hi; lw $P,lo($H); OP $V,off($P)
                # [; addiu $V,$V,imm; OP $V,off($P)]`) is self-contained.
                # Registers are per-site: P = this load's dest, H = this
                # load's base (the lui'd hi), V = the through-op's dest.
                nxt = insns[k + 1] if k + 1 < n else None
                gpf = None
                if nxt is not None and nxt.mnemonic in ("lb", "lbu", "lh",
                                                        "lhu", "lw"):
                    nt = G.toks_of(nxt)
                    if nt and G.rname(nt[1][2]) == dst:
                        noff = nt[1][1] if isinstance(nt[1][1], int) else int(nt[1][1], 0)
                        V = G.rname(nt[0][1])
                        H = basereg
                        hi_s = "0x%X" % int(base[2])
                        # RMW lookahead: addiu V,V,imm then sb/sh V,noff($P)
                        rmw = None
                        if (k + 3 < n and V in (2, 3, 4, 5, 6)
                                and insns[k + 2].mnemonic == "addiu"):
                            at = G.toks_of(insns[k + 2])
                            if (G.rname(at[0][1]) == V
                                    and G.rname(at[1][1]) == V):
                                st = G.toks_of(insns[k + 3]) if k + 3 < n else None
                                if (st and insns[k + 3].mnemonic in ("sb", "sh")
                                        and G.rname(st[0][1]) == V
                                        and G.rname(st[1][2]) == dst
                                        and (st[1][1] if isinstance(st[1][1], int)
                                             else int(st[1][1], 0)) == noff):
                                    aimm = at[2][1]
                                    if isinstance(aimm, str):
                                        aimm = int(aimm, 0)
                                    if aimm < 0:
                                        aimm += 0x10000
                                    rmw = (insns[k + 3].mnemonic, aimm)
                        if rmw and H in (2, 3, 4, 5, 6) and V in (2, 3, 4, 5, 6):
                            nm, df = rmw_macro(rmw[0], dst, H, V)
                            ctx.gp_def(nm, df)
                            # Emit as a statement: the STORE is a side
                            # effect.  The macro's value is NOT captured —
                            # capturing would re-evaluate if V is read
                            # again; a later cold read of V rejects safely.
                            emit(f"{nm}({hi_s}, {foff(off)}, {foff(noff)}, "
                                 f"{rmw[1]});")
                            env[dst] = ("val", "u32",
                                        f"*(volatile u32 *)0x{addr & 0xFFFFFFFF:X}", None)
                            k += 4
                            continue
                        pair = None
                        if (k + 3 < n and insns[k + 2].mnemonic == "dsll32"
                                and insns[k + 3].mnemonic == "dsra32"):
                            pair = insns[k + 2].op_str.split(",")[-1].strip()
                        if H in (2, 3, 4, 5, 6) and V in (2, 3, 4, 5, 6):
                            if pair in ("0x18", "24") and V == G.rname(
                                    G.toks_of(insns[k + 2])[0][1]):
                                nm, df = gp_macro_def("lbw", dst, H, V)
                                ctx.gp_def(nm, df)
                                env[V] = ("val", "s32",
                                          f"{nm}({hi_s}, {foff(off)}, {foff(noff)})", None)
                                if dst != V:
                                    env[dst] = ("val", "u32",
                                                f"*(volatile u32 *)0x{addr & 0xFFFFFFFF:X}", None)
                                k += 4
                                continue
                            if pair in ("0x10", "16") and V == G.rname(
                                    G.toks_of(insns[k + 2])[0][1]):
                                nm, df = gp_macro_def("lhw", dst, H, V)
                                ctx.gp_def(nm, df)
                                env[V] = ("val", "s32",
                                          f"{nm}({hi_s}, {foff(off)}, {foff(noff)})", None)
                                if dst != V:
                                    env[dst] = ("val", "u32",
                                                f"*(volatile u32 *)0x{addr & 0xFFFFFFFF:X}", None)
                                k += 4
                                continue
                            kind = nxt.mnemonic
                            nm, df = gp_macro_def(kind, dst, H, V)
                            ctx.gp_def(nm, df)
                            k2 = {"lb": "s32", "lh": "s32"}.get(kind, "u32")
                            env[V] = ("val", k2,
                                      f"{nm}({hi_s}, {foff(off)}, {foff(noff)})", None)
                            if dst != V:
                                # keep the pointer only when it lives in a
                                # DIFFERENT register than the loaded value
                                env[dst] = ("val", "u32",
                                            f"*(volatile u32 *)0x{addr & 0xFFFFFFFF:X}", None)
                            k += 2
                            continue
                ct = {"lw": "u32", "lbu": "u8", "lhu": "u16", "lh": "s16",
                      "lb": "s8"}[m]
                expr = f"*(volatile {ct} *)0x{addr & 0xFFFFFFFF:X}"
                spare = ("abs", m, basereg, dst, int(base[2]), off) \
                    if m in ("lb", "lh") else None
                env[dst] = ("val", "u32" if ct not in ("s16", "s8") else "s32",
                            expr, spare)
            else:
                raise G.Stop("load-base:" + str(base[1]))
            if (m in ("lb", "lh") and k + 2 < n
                    and insns[k + 1].mnemonic == "dsll32"
                    and insns[k + 2].mnemonic == "dsra32"):
                sh = insns[k + 1].op_str.split(",")[-1].strip()
                if {"0x18", "24", "0x10", "16"} & {sh}:
                    # CHAIN-DIRECT load + widen pair (Addendum 22): fuse the
                    # pair in-place on the load's own per-site dst (or the
                    # pair's split dst) — no SP_w plain-var temp (those get
                    # gcc homes + copies).  Base = this config's {B}.
                    base_e0 = env.get(dst)
                    if base_e0 is not None:
                        m0 = re.match(r"^SP_L([HB])0_R(\d)\(", base_e0[2])
                        if m0:
                            t2w = G.toks_of(insns[k + 1])
                            wdst = G.rname(t2w[0][1]) if t2w else dst
                            if wdst not in (2, 3, 4, 5, 6) or \
                                    dst not in (2, 3, 4, 5, 6):
                                raise G.Stop(f"cw-reg:{dst}/{wdst}")
                            op = "LB" if m0.group(1) == "B" else "LH"
                            shn = "0x18" if sh in ("0x18", "24") else "0x10"
                            if wdst == dst:
                                nm = f"SP_{op}WI0_T{dst}"
                                df = (f"#define {nm}(k) ({{ register s32 r "
                                      f"asm(\"${dst}\"); __asm__ volatile("
                                      f"\"lui {ctx.base},0x7000\\n\\t"
                                      f"{op.lower()} ${dst},\" #k \"({ctx.base})"
                                      f"\\n\\tdsll32 ${dst},${dst},{shn}"
                                      f"\\n\\tdsra32 ${dst},${dst},{shn}\" : "
                                      f"\"=r\"(r)); r; }})")
                                ctx.gp_def(nm, df)
                                env[dst] = ("val", "s32",
                                            f"{nm}({foff(off)})", None)
                            else:
                                # split dst: raw load stays live in $dst —
                                # pin only the WIDEN over the raw expression
                                nm = f"SP_{op}WI_T{wdst}"
                                df = (f"#define {nm}(v) ({{ register s32 r "
                                      f"asm(\"${wdst}\"); __asm__ volatile("
                                      f"\"dsll32 %0,%1,{shn}"
                                      f"\\n\\tdsra32 %0,%0,{shn}\" : "
                                      f"\"=r\"(r) : \"r\"(v)); r; }})")
                                ctx.gp_def(nm, df)
                                env[wdst] = ("val", "s32",
                                             f"{nm}({base_e0[2]})", None)
                            k += 3
                            continue
                    # STORE-FUSION: lb/lh; dsll32; dsra32; lui; sw ->
                    # SP_SW_W8/W16(off, load_expr).  The original keeps the
                    # widen pair and the store as one contiguous block; a
                    # separate SP_W16TO temp would change register choices.
                    if (k + 4 < n and insns[k + 3].mnemonic == "lui"
                            and insns[k + 4].mnemonic == "sw"):
                        t2 = G.toks_of(insns[k + 1])
                        wdst = G.rname(t2[0][1]) if t2 else dst
                        t4 = G.toks_of(insns[k + 4])
                        t3 = G.toks_of(insns[k + 3])
                        if (t4 and t3 and G.rname(t4[0][1]) == wdst
                                and G.rname(t3[0][1]) == G.rname(t4[1][2])):
                            le = env.get(dst)
                            if le is None:
                                raise G.Stop("fused-store-noexpr")
                            # Per-site scratch: emit the variant whose
                            # fixed widen register matches the ORIGINAL's
                            # dsll32 destination.  Scratch == chain base is
                            # FINE: the R-variant re-establishes the base
                            # with a fresh lui after consuming the scratch.
                            if wdst not in (2, 3, 4, 5, 6):
                                raise G.Stop(f"widen-scratch:{wdst}")
                            fam = "SP_SW_W8" if sh in ("0x18", "24") else "SP_SW_W16"
                            t3imm = int(t3[1][1], 0)
                            t3dst = G.rname(t3[0][1])
                            if t3imm == 0x7000:
                                # scratchpad store: BOTH registers come
                                # from the original's insns (scratch =
                                # pair dst, base = the store's own chain
                                # lui dst) — a two-reg literal macro.
                                # Single-reg variants collided (lui
                                # clobbered the widened value) and the
                                # config-base fallback mis-paired regs.
                                if t3dst not in (2, 3, 4, 5, 6) or \
                                        wdst not in (2, 3, 4, 5, 6) or \
                                        t3dst == wdst:
                                    raise G.Stop(f"wsf-reg:{t3dst}/{wdst}")
                                nm = f"SP_{fam.split('_')[-1]}_WS{wdst}B{t3dst}"
                                df = (f"#define {nm}(off, v) __asm__ volatile("
                                      f"\"dsll32 ${wdst},%0,{sh}"
                                      f"\\n\\tdsra32 ${wdst},${wdst},{sh}"
                                      f"\\n\\tlui ${t3dst},0x7000"
                                      f"\\n\\tsw ${wdst},\" #off \"(${t3dst})\" "
                                      f":: \"r\"(v) : \"${t3dst}\", \"${wdst}\")")
                                ctx.gp_def(nm, df)
                                emit(f"{nm}({foff(t4[1][1])}, {le[2]});")
                            else:
                                # absolute-global store: pin BOTH the base
                                # register and the hi immediate; widen
                                # scratch stays in the pair's own dst
                                # (single-reg variants clobbered the
                                # widened value with the base lui)
                                if t3dst not in (2, 3, 4, 5, 6):
                                    raise G.Stop(f"abs-store-base:{t3dst}")
                                nm, df = abs_ws_macro_def(
                                    "w8" if sh in ("0x18", "24") else "w16",
                                    t3dst, wdst)
                                ctx.gp_def(nm, df)
                                emit(f"{nm}({'0x%X' % t3imm}, {foff(t4[1][1])}, {le[2]});")
                            k += 5
                            continue
                    base_e = env.get(dst)
                    sp = base_e[3] if base_e else None
                    t2w = G.toks_of(insns[k + 1])
                    wdst = G.rname(t2w[0][1]) if t2w else dst
                    # chain2 / abs fused loads fire for ANY consumer
                    # (Addendum 22): the pair's dest is known, so the
                    # widened value never needs an SP_w plain-var temp.
                    if sp and sp[0] == "chain2":
                        _, k2m, kB, kD, kch, koff = sp
                        if (wdst not in (2, 3, 4, 5, 6)
                                or kB not in (2, 3, 4, 5, 6)
                                or kD not in (2, 3, 4, 5, 6)):
                            raise G.Stop(f"chain2-reg:{kB}/{kD}/{wdst}")
                        kind = "lbw" if k2m == "lb" else "lhw"
                        nm, df = chain2_macro_def(kind, kB, kD, wdst)
                        ctx.gp_def(nm, df)
                        env[wdst] = ("val", "s32",
                                     f"{nm}(0x{kch:X}, {foff(koff)})", None)
                        if wdst != dst:
                            env.pop(dst, None)
                        k += 3
                        continue
                    if sp and sp[0] == "abs":
                        _, k2m, kB, kD, khi, koff = sp
                        if (wdst not in (2, 3, 4, 5, 6)
                                or kB not in (2, 3, 4, 5, 6)
                                or kD not in (2, 3, 4, 5, 6)):
                            raise G.Stop(f"absf-reg:{kB}/{kD}/{wdst}")
                        nm, df = abs_fused_macro_def(k2m, kB, kD, wdst,
                                                     khi, koff)
                        ctx.gp_def(nm, df)
                        env[wdst] = ("val", "s32", nm, None)
                        if wdst != dst:
                            env.pop(dst, None)
                        k += 3
                        continue
                    nxt = insns[k + 3] if k + 3 < n else None
                    if (dst not in ARG_REGS and nxt is not None
                            and nxt.mnemonic in ("andi", "ori", "xori",
                                                 "sll", "sra", "srl",
                                                 "addiu", "slt")):
                        fused = "SP_LBW" if m == "lb" else "SP_LHW"
                        mm2 = (re.match(r"^SP_LB0?\(0x([0-9A-F]+)", base_e[2])
                               if base_e else None)
                        if not mm2:
                            # Addendum 37: tied-atom loads fall through to
                            # the generic pair path — SP_W8TO on the atom
                            # emits the SAME dsll32/dsra32 pair; the old
                            # text re-fusion is legacy (pre-atom era) and
                            # its hard Stop blocked ~374x3 candidates.
                            pass
                        else:
                            ch2 = int(mm2.group(1), 16)
                            env[dst] = ("val", "s32",
                                        f"{fused}(0x{ch2:X}, {foff(off)})", None)
                            k += 3
                            continue
                    # The widen pair may be SPLIT: dsll32 $wdst,$dst,0x10
                    # writes a different register than the load's destination.
                    # Register the widened value under the pair's real dest.
                    t2 = G.toks_of(insns[k + 1])
                    wdst = G.rname(t2[0][1]) if t2 else dst
                    wpair(wdst, dst, sh)
                    k += 3
                    continue
            k += 1
            continue

        if m == "dsll32" and k + 1 < n and insns[k + 1].mnemonic == "dsra32":
            wpair(G.rname(t[0][1]), G.rname(t[1][1]),
                  i.op_str.split(",")[-1].strip())
            k += 2
            continue

        if m in ("addiu", "addu", "add", "subu", "sub", "andi", "ori", "xori",
                 "and", "or", "xor", "sll", "sra", "srl", "negu", "sllv",
                 "slt", "slti", "sltu", "sltiu"):
            dst = G.rname(t[0][1])
            src = G.rname(t[1][1]) if t[1][0] == "r" else None
            if src == 0:
                src = None
            if src is None and m == "addiu" and t[1][1] == "zero":
                imm = int(t[2][1], 0)
                if imm >= 0x8000:
                    imm -= 0x10000
                if dst in (2, 3):
                    # pinned constant materialization (the original's li
                    # register is visible; gcc would otherwise pick).
                    # Tied AT ITS POSITION (Addendum 29): the original's
                    # li runs before following chain loads.
                    nm, df = li_t_macro_def(dst)
                    ctx.gp_def(nm, df)
                    atom = tie_at(dst, f"{nm}({imm})")
                    env[dst] = ("val", "u32", atom, None)
                else:
                    setreg(dst, ("val", "u32", str(imm), None))
                k += 1
                continue
            e = env.get(src) if src is not None else None
            if e is None:
                raise G.Stop("alu-cold:" + m)
            E = e[2]
            imm = None
            if len(t) == 3 and t[2][0] == "i":
                imm = int(t[2][1], 0)
                if m not in ("andi", "ori", "xori") and imm >= 0x8000:
                    imm -= 0x10000
            if e[1] == "hi" and m == "addiu" and imm is not None:
                if dst in (2, 3):
                    nm, df = addr_t_macro_def(dst)
                    ctx.gp_def(nm, df)
                    atom = tie_at(dst, f"{nm}(0x{int(E):X}, {imm & 0xFFFF})")
                    env[dst] = ("val", "u32", atom, None)
                else:
                    setreg(dst, ("val", "u32",
                                 f"SP_ADDR(0x{int(E):X}, {foff(imm)})", None))
            elif m == "addiu" and imm is not None:
                if dst in (2, 3):
                    nm, df = alu_t_macro_def("addiu", dst)
                    ctx.gp_def(nm, df)
                    atom = tie_at(dst, f"{nm}({E}, {imm})")
                    env[dst] = ("val", "u32", atom, None)
                else:
                    setreg(dst, ("val", "u32",
                                 f"SP_ADDIU({E}, {foff(imm)})", None))
            elif m in ("addiu", "addu", "add") and imm is None:
                e2 = env.get(G.rname(t[2][1]))
                if e2 is None:
                    raise G.Stop("add-reg-cold")
                # hi-kind operand = a lui'd constant: emit the pinned
                # materialize+addu pair (constant into ITS OWN register,
                # plain addu — the fold made gcc use $at + daddu)
                if (e2[1] == "hi" or e[1] == "hi") and \
                        dst in (2, 3, 4, 5, 6):
                    hi_e, other = (e2, E) if e2[1] == "hi" else (e, e2[2])
                    H = hi_e[3]
                    if H is not None and H in (2, 3, 4, 5, 6):
                        hi_first = (hi_e is e)
                        nm, df = hi_addu_macro_def(dst, H, hi_first)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32",
                                     f"{nm}({hi_e[2]}, {other})", None))
                        k += 1
                        continue
                E2n = (f"((u32)({e2[2]}) << 16)" if e2[1] == "hi"
                       else e2[2])
                En = (f"((u32)({E}) << 16)" if e[1] == "hi" else E)
                if dst in (2, 3):
                    nm, df = alu_t_macro_def("addu", dst, two=True)
                    ctx.gp_def(nm, df)
                    setreg(dst, ("val", "u32",
                                 f"{nm}({En}, {E2n})", None))
                else:
                    setreg(dst, ("val", "u32", f"({En} + {E2n})", None))
            elif m in ("subu", "sub"):
                if dst in (2, 3):
                    nm, df = alu_t_macro_def("subu", dst)
                    ctx.gp_def(nm, df)
                    setreg(dst, ("val", "u32", f"{nm}({E}, {imm})", None))
                else:
                    setreg(dst, ("val", "u32", f"({E} - {imm})", None))
            elif m in ("andi", "and"):
                if imm is None:
                    e2 = env.get(G.rname(t[2][1]))
                    if e2 is None:
                        raise G.Stop("alu2-cold")
                    # Addendum 40: pinned reg-reg and
                    if dst in (2, 3, 5, 6):
                        nm, df = alu_t_macro_def("and", dst, two=True)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32",
                                     f"{nm}({E}, {e2[2]})", None))
                    else:
                        setreg(dst, ("val", "u32", f"({E} & {e2[2]})", None))
                else:
                    if e[1] == "hi":
                        E = f"((u32)({E}) << 16)"
                    hreg = e[3] if e[1] == "hi" else None
                    if hreg is not None and hreg in (2, 3, 4, 5, 6) \
                            and dst in (2, 3, 4, 5, 6):
                        nm, df = hi_op_macro_def("andi", dst, hreg)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32",
                                     f"{nm}({int(e[2])}, {imm})", None))
                    elif dst in (2, 3):
                        nm, df = alu_t_macro_def("andi", dst)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32", f"{nm}({E}, {imm})", None))
                    else:
                        setreg(dst, ("val", "u32", f"SP_ANDI({E}, {'0x%X' % imm})", None))
            elif m in ("ori", "or"):
                if imm is None:
                    e2 = env.get(G.rname(t[2][1]))
                    if e2 is None:
                        raise G.Stop("alu2-cold")
                    # Addendum 40: pinned reg-reg or
                    if dst in (2, 3, 5, 6):
                        nm, df = alu_t_macro_def("or", dst, two=True)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32",
                                     f"{nm}({E}, {e2[2]})", None))
                    else:
                        setreg(dst, ("val", "u32", f"({E} | {e2[2]})", None))
                else:
                    if e[1] == "hi":
                        # lui'd hi + ori: C ((u32)hi << 16) folds to the
                        # constant, gcc materializes it with lui (matching
                        # the original's lui/ori pair)
                        E = f"((u32)({E}) << 16)"
                    hreg = e[3] if e[1] == "hi" else None
                    if hreg is not None and hreg in (2, 3, 4, 5, 6) \
                            and dst in (2, 3, 4, 5, 6):
                        nm, df = hi_op_macro_def("ori", dst, hreg)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32",
                                     f"{nm}({int(e[2])}, {imm})", None))
                    elif dst in (2, 3):
                        nm, df = alu_t_macro_def("ori", dst)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32", f"{nm}({E}, {imm})", None))
                    else:
                        setreg(dst, ("val", "u32", f"SP_ORI({E}, {'0x%X' % imm})", None))
            elif m in ("xori", "xor"):
                if imm is None:
                    e2 = env.get(G.rname(t[2][1]))
                    if e2 is None:
                        raise G.Stop("alu2-cold")
                    # Addendum 40: pinned reg-reg xor
                    if dst in (2, 3, 5, 6):
                        nm, df = alu_t_macro_def("xor", dst, two=True)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32",
                                     f"{nm}({E}, {e2[2]})", None))
                    else:
                        setreg(dst, ("val", "u32", f"({E} ^ {e2[2]})", None))
                else:
                    if e[1] == "hi":
                        E = f"((u32)({E}) << 16)"
                    hreg = e[3] if e[1] == "hi" else None
                    if hreg is not None and hreg in (2, 3, 4, 5, 6) \
                            and dst in (2, 3, 4, 5, 6):
                        nm, df = hi_op_macro_def("xori", dst, hreg)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32",
                                     f"{nm}({int(e[2])}, {imm})", None))
                    elif dst in (2, 3):
                        nm, df = alu_t_macro_def("xori", dst)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32", f"{nm}({E}, {imm})", None))
                    else:
                        setreg(dst, ("val", "u32", f"SP_XORI({E}, {'0x%X' % imm})", None))
            elif m == "sll":
                if dst in (2, 3):
                    nm, df = alu_t_macro_def("sll", dst)
                    ctx.gp_def(nm, df)
                    setreg(dst, ("val", "u32", f"{nm}({E}, {imm})", None))
                else:
                    setreg(dst, ("val", "u32", f"SP_SLL({E}, {'0x%X' % imm})", None))
            elif m in ("sra", "srl"):
                sop = "sra" if m == "sra" else "srl"
                if dst in (2, 3):
                    nm, df = alu_t_macro_def(sop, dst)
                    ctx.gp_def(nm, df)
                    setreg(dst, ("val", "u32", f"{nm}({E}, {imm})", None))
                elif sop == "srl":
                    setreg(dst, ("val", "u32", f"SP_SRL({E}, {'0x%X' % imm})", None))
                else:
                    setreg(dst, ("val", "u32", f"SP_SRA({E}, {'0x%X' % imm})", None))
            elif m == "negu":
                # negu $d,$s = 0 - $s; C unary minus on the u32 expr makes
                # gcc emit subu $d,$zero,$s (the negu opcode)
                setreg(dst, ("val", "u32", f"(-({E}))", None))
            elif m == "sllv":
                # variable shift: both operands must be live
                e2 = env.get(G.rname(t[2][1]))
                if e2 is None:
                    raise G.Stop("sllv-cold")
                # Addendum 40: pinned for pinned dsts (gcc picks its own
                # regs from a plain C shift — the original's sllv dst is
                # visible; 00253580 class)
                if dst in (2, 3, 5, 6):
                    nm, df = alu_t_macro_def("sllv", dst, two=True)
                    ctx.gp_def(nm, df)
                    setreg(dst, ("val", "u32", f"{nm}({E}, {e2[2]})", None))
                else:
                    setreg(dst, ("val", "u32", f"({E} << {e2[2]})", None))
            elif m in ("slt", "slti"):
                # Addendum 39: unsigned/signed compares — pinned T-macros
                # (gcc would otherwise reorder the compare with its inputs)
                cop = "slt"
                if imm is not None:
                    if dst in (2, 3, 5, 6):
                        nm, df = alu_t_macro_def(cop, dst)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32", f"{nm}({E}, {imm})", None))
                    else:
                        setreg(dst, ("val", "u32",
                                     f"(u32)((s32)({E}) < {imm})", None))
                else:
                    e2 = env.get(G.rname(t[2][1]))
                    if e2 is None:
                        raise G.Stop("slt-cold")
                    if dst in (2, 3, 5, 6):
                        nm, df = alu_t_macro_def(cop, dst, two=True)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32",
                                     f"{nm}({E}, {e2[2]})", None))
                    else:
                        setreg(dst, ("val", "u32",
                                     f"(u32)((s32)({E}) < ({e2[2]}))", None))
            elif m in ("sltu", "sltiu"):
                cop = "sltu"
                if imm is not None:
                    if dst in (2, 3, 5, 6):
                        nm, df = alu_t_macro_def("sltiu", dst)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32", f"{nm}({E}, {imm})", None))
                    else:
                        setreg(dst, ("val", "u32",
                                     f"(u32)(({E}) < {imm})", None))
                else:
                    e2 = env.get(G.rname(t[2][1]))
                    if e2 is None:
                        raise G.Stop("sltu-cold")
                    if dst in (2, 3, 5, 6):
                        nm, df = alu_t_macro_def(cop, dst, two=True)
                        ctx.gp_def(nm, df)
                        setreg(dst, ("val", "u32",
                                     f"{nm}({E}, {e2[2]})", None))
                    else:
                        setreg(dst, ("val", "u32",
                                     f"(u32)(({E}) < ({e2[2]}))", None))
            else:
                raise G.Stop("alu:" + m)
            k += 1
            continue

        if m == "move":
            dst = G.rname(t[0][1])
            src = G.rname(t[1][1])
            if src == 0:
                setreg(dst, ("val", "u32", "0", None))
            elif src in env:
                setreg(dst, env[src])
            else:
                raise G.Stop("move-cold")
            k += 1
            continue

        if m in ("sw", "sb", "sh"):
            srcreg = t[0][1]
            off, basereg = t[1][1], G.rname(t[1][2])
            base = env.get(basereg)
            if base is None or base[1] not in ("chain", "sp", "hi", "u32"):
                raise G.Stop(f"store-base@{i.address:08X}:{m}:{basereg}:{off:#x}")
            if srcreg == "zero":
                if base[1] == "hi":
                    emit(f"SP_SW0_ABS_R{basereg}({'0x%X' % int(base[2])}, {foff(off)});")
                    k += 1
                    continue
                if base[1] == "sp":
                    raise G.Stop(f"sp-store@{i.address:08X}:{m}:{off:#x}")
                if base[1] == "u32":
                    # Zero store THROUGH A LOADED POINTER (Addendum 30):
                    # was rendered as a chain SP_SW0 — wrong base (the
                    # original stores off the loaded pointer, no lui).
                    if basereg not in (2, 3, 4, 5, 6):
                        raise G.Stop(f"ptr-store-base:{basereg}")
                    pnm, pdf = zptr_store_macro_def(m, basereg)
                    ctx.gp_def(pnm, pdf)
                    emit(f"{pnm}({base[2]}, {foff(off)});")
                    k += 1
                    continue
                # Addendum 30: per-site at the ORIGINAL's width (sb/sh zero
                # stores were rendered as the word form)
                znm, zdf = zstore_macro_def(m, basereg)
                ctx.gp_def(znm, zdf)
                emit(f"{znm}({foff(off)});")
                k += 1
                continue
            se = env.get(G.rname(srcreg))
            if se is None:
                rn = G.rname(srcreg)
                if rn in ARG_REGS:
                    E = param_of(rn)
                    kind = "arg"       # cold incoming argument; not a wraw value
                else:
                    raise G.Stop(f"store-cold-val@{i.address:08X}:{m}:src=${srcreg}:base={basereg}:{off:#x}")
            else:
                E = se[2]
                kind = se[1]
            if kind == "hi":
                # a lui'd constant used DIRECTLY as a value: a pinned-home
                # hi was materialized at its lui's position (Addendum
                # 30/34) — use that register; otherwise fold so gcc
                # materializes it
                if se is not None and (se[3] in ARG_REGS or se[3] in (2, 3, 5, 6)):
                    E = (ARG_REGS[se[3]] if se[3] in ARG_REGS
                         else f"SP_r{se[3]}")
                else:
                    E = f"((u32)({E}) << 16)"
            direct = base[2] == "SP"
            if base[1] == "hi":
                # Absolute-global store: base register holds a lui'd hi.
                # Per-site pinned macro (register + hi from the original).
                fam = {"sw": "SP_SW_ABS", "sb": "SP_SB_ABS",
                       "sh": "SP_SH_ABS"}[m]
                emit(f"{fam}_R{basereg}({'0x%X' % int(base[2])}, {foff(off)}, {E});")
                k += 1
                continue
            if base[1] == "u32":
                # Store through a pointer VALUE (p = *g_pStruct; p->f = x):
                # pin the pointer to the original's register, store off it;
                # the VALUE's pinned register initializes first (insn order)
                if basereg not in (2, 3, 4, 5, 6):
                    raise G.Stop(f"ptr-store-base:{basereg}")
                srcreg2 = G.rname(srcreg)
                v = srcreg2 if srcreg2 in (2, 3, 4, 5, 6) else None
                nm, df = ptr_store_macro(m, basereg, v)
                ctx.gp_def(nm, df)
                emit(f"{nm}(({base[2]}), {foff(off)}, {E});")
                k += 1
                continue
            if kind == "wraw":
                macro = "SP_SW_W8" if se[3] == "w8" else "SP_SW_W16"
                emit(f"{macro}({foff(off)}, {E});")
            else:
                # Unified base choice (Addendum 22): the store base must
                # not collide with the value's pinned register — gcc emits
                # the chain lui before the value is consumed otherwise
                # (semantically broken order, 00223940-class).
                vm = (re.search(r"_T(\d)\(", E) or re.search(r"_R(\d)\(", E))
                valreg = int(vm.group(1)) if vm else None
                if valreg is not None and basereg == valreg:
                    basereg2 = 3 if basereg == 2 else 2
                else:
                    basereg2 = basereg
                letter = {"sw": "SW", "sb": "SB", "sh": "SH"}[m]
                if basereg2 in (2, 3):
                    emit(f"SP_{letter}_R{basereg2}({foff(off)}, {E});")
                else:
                    emit(f"{'SP_' + letter + '_D' if direct else 'SP_' + letter}({foff(off)}, {E});")
            k += 1
            continue

        if m == "jal":
            args = [ARG_REGS[rn] for rn in sorted(ARG_REGS) if rn in ctx.used_args]
            nc[0] += 1
            rv = f"SP_rv{nc[0]}"
            acts.append(("mdecl", f"u32 {rv};"))
            acts.append(("mstmt",
                         f"{rv} = func_{int(i.op_str, 0):08X}({', '.join(args)});"))
            env[2] = ("val", "u32", rv, None)
            for rn in ARG_REGS:
                env.pop(rn, None)
            k += 1
            continue

        if m == "jalr":
            r = G.rname(t[-1][1])
            e = env.get(r)
            if e is None or e[1] != "u32":
                raise G.Stop("jalr-target")
            nc[0] += 1
            rv = f"SP_rv{nc[0]}"
            acts.append(("mdecl", f"u32 {rv};"))
            if e[2].isdigit():
                acts.append(("mstmt", f"{rv} = ((u32 (*)())0x{int(e[2], 0):08X})();"))
            else:
                acts.append(("mstmt", f"{rv} = ((u32 (*)())({e[2]}))();"))
            env[2] = ("val", "u32", rv, None)
            k += 1
            continue

        if m in ("beq", "bne", "blez", "bgtz", "bltz", "bgez", "j", "b"):
            raise G.Stop("branch-in-run:" + m)

        raise G.Stop(f"insn:{m}@{i.address:08X}")
    return acts, env


def macro_extract_cond(producer, branch, env, run_acts):
    if branch.mnemonic in ("beq", "bne"):
        # register-compare: BOTH operands come from the branch itself
        # (the producer mechanism does not apply); the comparand is
        # typically a constant materialized by addiu $r,$zero,imm in the
        # same run, which gcc re-emits as li+beq, byte-identical.
        bt = G.toks_of(branch)
        e1 = env.get(G.rname(bt[0][1]))
        e2 = env.get(G.rname(bt[1][1]))
        if (e1 is None or e1[0] != "val" or e2 is None or e2[0] != "val"):
            raise G.Stop("cond-env2")
        kind = "eq" if branch.mnemonic == "beq" else "ne"
        # pin the comparand register when the original used a scratch
        # (gcc otherwise picks its own li register -> nibble diff)
        cr = G.rname(bt[1][1])
        if cr in (2, 3, 4, 5, 6) and cr != G.rname(bt[0][1]):
            return ("mtest2", e1[2], e2[2], kind, cr)
        return ("mtest2", e1[2], e2[2], kind, None)
    t = G.toks_of(producer)
    if not t or t[0][0] != "r" or len(t) < 2:
        # capstone can yield odd producer decodes (dropped MMI prefixes,
        # unmacroed ops); a clean reject, not a crash
        raise G.Stop("cond-producer-form")
    dst = G.rname(t[0][1])
    e = env.get(dst)
    if e is None or e[0] != "val":
        raise G.Stop("cond-env")
    # kind = the C condition whose branch-over-the-body reproduces the
    # insn: beqz skips when x==0 (body runs when nonzero) -> if (x);
    # bnez -> if (!x); bgez skips when x>=0 -> if ((s32)x < 0);
    # bltz -> if ((s32)x >= 0); blez -> > 0; bgtz -> <= 0.
    # (The old bgez->ge0 mapping emitted the INVERSE branch: gcc writes
    # bltz for `if (x >= 0)`, a 1-byte diff.  beqz/bnez were always right,
    # which is why only sign-tested conditions landed in the near-miss pool.)
    opmap = {"beqz": "bool1", "bnez": "bool0", "bgez": "lt0", "bltz": "ge0",
             "blez": "gt0", "bgtz": "le0"}
    kind = opmap.get(branch.mnemonic)
    if kind is None:
        raise G.Stop("cond-branch:" + branch.mnemonic)
    return ("mtest", e[2], kind)


def structure_local(insns, va, size):
    """G.structure/structure_region without the control-transfer pre-scans
    (the decoder itself rejects unrepresentable control flow)."""
    import bisect

    def region(body, va_lo, va_hi, env, nc, alias, crosses=None):
        # crosses accumulates (branch_target, if_node) for every if built in
        # this function; a nested branch whose target is an ENCLOSING if's
        # else-entry means the original source had a duplicate else arm
        # (gcc cross-jumping merged the copies) — the parent attaches its
        # else segs to that child after the recursion returns.
        if crosses is None:
            crosses = []
        segs = []
        run_start = 0
        i = 0
        n = len(body)
        addrs = [x.address for x in body]

        def idx_of(a):
            return bisect.bisect_left(addrs, a)

        while i < n:
            ins = body[i]
            if ins.mnemonic in G.BRANCH_OPS or ins.mnemonic in ("beq", "bne"):
                if i + 1 >= n or body[i + 1].mnemonic != "nop":
                    raise G.Stop(f"delay-slot@{ins.address:08X}")
                tgt = G.branch_target(ins)
                if tgt is None or not (va_lo <= tgt <= va_hi):
                    raise G.Stop(f"branch-target-out@{ins.address:08X}")
                if tgt <= ins.address:
                    raise G.Stop("backward-branch")
                tidx = idx_of(tgt)
                if tidx >= n and tgt != va_hi:
                    raise G.Stop(f"branch-target-miss@{ins.address:08X}")
                if tidx <= i + 1:
                    tidx = i + 2
                then = body[i + 2:tidx]
                else_segs = None
                else_env = None
                join_idx = tidx
                inverted = False
                then_hi = tgt
                if (ins.mnemonic == "beq" and len(then) >= 2
                        and then[-2].mnemonic == "b"
                        and then[-1].mnemonic == "nop"):
                    # INVERTED if (gcc if-else-if cascade): beq jumps TO the
                    # body when true; the fallthrough is the else/next check
                    # ending in a jump to the join.  then = [tgt..join),
                    # clipped to this region's body (a parent's tail block
                    # beyond it belongs to the parent's own then).
                    try:
                        j = int(then[-2].op_str, 0)
                    except ValueError:
                        j = None
                    if j is not None and tidx < j <= va_hi:
                        jidx = idx_of(j)
                        if jidx > n:
                            jidx = n
                        if jidx <= tidx:
                            raise G.Stop("else-join-miss")
                        else_insns = then[:-2]
                        then = body[tidx:jidx]
                        join_idx = jidx
                        inverted = True
                        then_hi = j
                        if else_insns:
                            try:
                                else_segs, else_env = region(
                                    else_insns, else_insns[0].address, j,
                                    dict(env), nc, alias, crosses)
                            except G.Stop as e:
                                raise G.Stop(f"{e} <else-of-{ins.address:08X}>")
                            if not else_segs or all(s == ("acts", [])
                                                    for s in else_segs):
                                raise G.Stop("empty-else")
                if (not inverted and len(then) >= 2
                        and then[-2].mnemonic == "b"
                        and then[-1].mnemonic == "nop"):
                    try:
                        j = int(then[-2].op_str, 0)
                    except ValueError:
                        j = None
                    if j is not None and tidx < j <= va_hi:
                        jidx = idx_of(j)
                        if jidx > n:
                            jidx = n
                        if jidx <= tidx:
                            raise G.Stop("else-join-miss")
                        else_insns = body[tidx:jidx]
                        try:
                            else_segs, else_env = region(
                                else_insns, tgt, j, dict(env), nc, alias, crosses)
                        except G.Stop as e:
                            raise G.Stop(f"{e} <else-of-{ins.address:08X}>")
                        if not else_segs or all(s == ("acts", []) for s in else_segs):
                            raise G.Stop("empty-else")
                        then = then[:-2]
                        join_idx = jidx
                if i == run_start:
                    raise G.Stop(f"branch-without-run@{ins.address:08X}")
                run = body[run_start:i]
                producer = body[i - 1]
                acts, env2 = G.decode_run(run, env, nc)
                env = env2
                cond = G.extract_cond(producer, ins, env, acts)
                if not inverted and cond[0] == "mtest2":
                    # Standard layout branches when FALSE (bne skips the
                    # body): the C polarity is the INVERSE of the mnemonic.
                    # Inverted ifs branch when TRUE and keep direct polarity.
                    _, E1, E2, k2, cr = cond
                    cond = ("mtest2", E1, E2,
                            "ne" if k2 == "eq" else "eq", cr)
                then_lo = then[0].address if then else ins.address
                try:
                    then_segs, then_env = region(then, then_lo, then_hi, dict(env),
                                                 nc, alias, crosses)
                except G.Stop as e:
                    raise G.Stop(f"{e} <then-of-{ins.address:08X}>")
                if else_segs is None:
                    for r, e2 in then_env.items():
                        if e2[0] != "val":
                            continue
                        if r in env and env[r][0] == "val":
                            alias[e2[2]] = env[r][2]
                        elif r not in env:
                            env[r] = e2
                else:
                    for r, e2 in then_env.items():
                        if e2[0] != "val" or r in env:
                            continue
                        if r in else_env and else_env[r] == e2:
                            env[r] = e2
                if not then_segs or all(s == ("acts", []) for s in then_segs):
                    raise G.Stop("empty-then")
                ifnode = ["if", cond, then_segs, else_segs]
                if inverted:
                    # 5th/6th slots: inverted marker + join address (the
                    # emitter shares one end-label per join address).
                    ifnode.append("inv")
                    ifnode.append(j)
                if else_segs is not None and not inverted:
                    # cross-jump: an earlier if whose branch targets THIS
                    # if's else-entry shares this else arm.  Emitting the
                    # arm twice does NOT re-merge (ee-gcc 2.96 won't), so
                    # the children get `goto lbl;` and this else carries
                    # the label — one shared block, like the original.
                    kids = [cnode for ctgt, cnode in crosses
                            if ctgt == tgt and cnode[0] == "if"
                            and cnode[3] is None]
                    if kids:
                        CTX.xj += 1
                        lbl = "SP_xj%d" % CTX.xj
                        for cnode in kids:
                            cnode[3] = [("xgoto", lbl)]
                        ifnode.append(lbl)
                segs.append(("acts", acts))
                if not inverted:
                    crosses.append((tgt, ifnode))
                segs.append(ifnode)
                run_start = join_idx
                i = join_idx
                continue
            if ins.mnemonic in ("j", "b"):
                raise G.Stop(f"uncond-jump@{ins.address:08X}")
            i += 1
        tail = body[run_start:i]
        tacts, env = G.decode_run(tail, env, nc)
        segs.append(("acts", tacts))
        return segs, env

    jr_idx = None
    for kk, x in enumerate(insns):
        if x.mnemonic == "jr":
            if "$ra" not in x.op_str:
                raise G.Stop("jr-non-ra")
            jr_idx = kk
            break
    if jr_idx is None:
        raise G.Stop("no-jr")
    if any(x.mnemonic != "nop" for x in insns[jr_idx + 1:]):
        raise G.Stop("code-after-jr")
    alias = {}
    body = insns[:jr_idx]
    # top-level va_hi = one past the last body insn: a branch targeting the
    # (frame-stripped) epilogue is a branch to the region's own end.
    top_hi = (body[-1].address + 4) if body else va
    segs, _ = region(body, va, top_hi, {}, [0], alias)
    return segs, alias


def build_macro_source(va, macros_text, segs, ctx):
    ctx_params = ctx.params
    stmts = []
    decls = list(ctx.decls)
    ext = []
    eseen = set()

    def emit(segs_, indent):
        for seg in segs_:
            if seg[0] == "xgoto":
                stmts.append("    " * indent + "goto " + seg[1] + ";")
                continue
            if seg[0] == "acts":
                for a in seg[1]:
                    if a[0] == "mdecl":
                        decls.append("    " + a[1])
                    elif a[0] == "mstmt":
                        stmts.append("    " * indent + a[1])
                    else:
                        l = "extern u32 func_%08X();" % a[1]
                        if l not in eseen:
                            eseen.add(l)
                            ext.append(l)
            else:
                _, cond, then_segs, else_segs = seg[:4]
                lbl = seg[4] if len(seg) > 4 else None
                if cond[0] == "mtest2":
                    _, E1, E2, k2, cr = cond
                    if cr is not None:
                        # pin the comparand to the original's li register
                        E2s = (f"({{ register u32 _c asm(\"${cr}\") = "
                               f"(u32)({E2}); _c; }})")
                    else:
                        E2s = f"({E2})"
                    if k2 == "eq":
                        text = f"if (({E1}) == {E2s})"
                    else:
                        text = f"if (({E1}) != {E2s})"
                else:
                    _, E, kind = cond
                    if kind == "bool0":
                        text = f"if (!({E}))"
                    elif kind == "bool1":
                        text = f"if ({E})"
                    elif kind == "ge0":
                        text = f"if ((s32)({E}) >= 0)"
                    elif kind == "lt0":
                        text = f"if ((s32)({E}) < 0)"
                    elif kind == "le0":
                        text = f"if ((s32)({E}) <= 0)"
                    else:
                        text = f"if ((s32)({E}) > 0)"
                if len(seg) > 4 and seg[4] == "inv":
                    # INVERTED if (beq-to-body cascade): emit the branch
                    # explicitly — `if (c) goto Lthen;` + else inline +
                    # `goto Lend;` + Lthen: then-body + Lend:.  One end
                    # label per join ADDRESS (nested ifs sharing the join
                    # borrow the outermost label; emit is outer-first).
                    J = seg[5]
                    if J not in CTX.xjlbl:
                        CTX.xjn += 1
                        CTX.xjlbl[J] = "SP_ce%d" % CTX.xjn
                        own = True
                    else:
                        own = False
                    lend = CTX.xjlbl[J]
                    CTX.xjn += 1
                    lthen = "SP_ct%d" % CTX.xjn
                    stmts.append("    " * indent + text + f" goto {lthen};")
                    if else_segs is not None:
                        emit(else_segs, indent)
                    stmts.append("    " * indent + f"goto {lend};")
                    stmts.append("    " * indent + f"{lthen}: ;")
                    emit(then_segs, indent + 1)
                    if own:
                        stmts.append("    " * indent + f"{lend}: ;")
                    continue
                stmts.append("    " * indent + text + " {")
                emit(then_segs, indent + 1)
                if else_segs is not None:
                    stmts.append("    " * indent + "} else {")
                    if lbl:
                        stmts.append("    " * (indent + 1) + lbl + ": ;")
                    emit(else_segs, indent + 1)
                stmts.append("    " * indent + "}")

    emit(segs, 1)
    if not stmts:
        raise G.Stop("empty-body")
    seen = set()
    dd = [d for d in decls if not (d in seen or seen.add(d))]
    head = macros_text
    if ctx.gp:
        head += "\n".join(ctx.gp) + "\n"
    head += "\n".join(ext) + "\n"
    if ctx_params:
        names = ", ".join(f"arg_a{r - 4}" for r in sorted(ctx_params))
        head += f"void func_{va:08X}({names})\n{{\n"
        for r in sorted(ctx_params):
            head += f"    u32 arg_a{r - 4};\n"
    else:
        head += f"void func_{va:08X}(void)\n{{\n"
    for d in dd:
        head += d + "\n"
    return head + "\n".join(stmts) + "\n}\n"


def main():
    G.decode_run = macro_decode_run
    G.extract_cond = macro_extract_cond
    global CTX
    if os.environ.get("PINNIFY"):
        # Addendum 20 backend v0: hoist nested macro calls into pinned
        # register-file tie statements (validated by hand on 00223500)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import pinnify as _pf
        def _pin(src):
            return _pf.pinnify_c(src)[0]
    else:
        _pin = None
    maxbytes = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    maxfuncs = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    matched = set(l.strip().split(":")[0].split("@")[0]
                  for l in open(f"{ROOT}/src_ro9/matched.txt") if l.strip())
    spec = []
    scanned = 0
    built = 0
    for s in sorted(glob.glob(f"{ROOT}/ro9/func_*.s")):
        stem = os.path.basename(s)[:-2]
        if stem in matched:
            continue
        va, size, insns = G.load_insns(stem)
        if size > maxbytes:
            continue
        if not any(i.mnemonic in G.WIDEN for i in insns):
            continue
        scanned += 1
        if len(insns) < size // 4:
            REJECT["mmi"] = REJECT.get("mmi", 0) + 1
            continue
        stripped = G.strip_call_frame(insns)
        if stripped is None:
            REJECT["frame"] = REJECT.get("frame", 0) + 1
            continue
        # no-call gate REMOVED (Addendum 35): the jal requirement was early
        # scoping — frameless widen functions without calls build the same
        # way (leaf bodies; jalr-only callers handled by the fpcall path)
        built_this = False
        for base, data in (("$3", "$3"), ("$2", "$2"), ("$2", "$3")):
            try:
                CTX = Ctx(base)
                segs, alias = structure_local(stripped, va, size)
                src = build_macro_source(va, macros_for(base, data), segs, CTX)
            except G.Stop as e:
                key = f"{base}/{data}: {e}"
                REJECT[key] = REJECT.get(key, 0) + 1
                continue
            if _pin:
                src = _pin(src)
            spec.append(f"VA {va:08X}\nSIZE {size:X}\nCOMP ee-gcc2.96\nEND\n{src}---\n")
            built_this = True
        if built_this:
            built += 1
        if built >= maxfuncs:
            break
    print(f"widen-fn scanned {scanned}, macro-built {built} (x2 bases)")
    coarse = Counter()
    for kk, v in REJECT.items():
        coarse[kk.split("@")[0].split(":")[-1] if "@" in kk else kk] += v
    print("rejects(coarse):", ", ".join(f"{k}={v}" for k, v in
          coarse.most_common(14)))
    cold = sorted(kk for kk in REJECT if "store-cold-val@" in kk)
    for kk in cold[:6]:
        print("  cold:", kk)
    sp = sorted(kk for kk in REJECT if "sp-store@" in kk or "store-base@" in kk)
    for kk in sp[:6]:
        print("  base:", kk)
    open(f"{ROOT}/pilots/spec_macro2.txt", "w").write("".join(spec))
    if not spec:
        return
    r = subprocess.run(["python3", f"{ROOT}/pilots/install_wins2.py",
                        f"{ROOT}/pilots/spec_macro2.txt"],
                       capture_output=True, text=True)
    ver = re.findall(r"VERIFIED (func_[0-9A-F]{8}) \[[^]]+\]: (MATCH(?:\+PAD)?)", r.stdout)
    rej = re.findall(r"REJECT (func_[0-9A-F]{8}) \[[^]]+\]: (.*)", r.stdout)
    print(f"VERIFIED {len(ver)}, REJECTED {len(rej)}")
    for w, v in sorted(set(ver)):
        print(f"WIN {w} {v}")
    rc = Counter(m.split(":")[0][:44] for _, m in rej)
    for kk, v in rc.most_common(8):
        print(f"  rej {v:3d}  {kk}")


if __name__ == "__main__":
    main()

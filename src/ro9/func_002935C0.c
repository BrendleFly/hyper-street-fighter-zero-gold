typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00293BE0();
extern void func_00293BE0();
extern void func_00293B10();
void func_002935C0(void)
{
    __asm {
        lui $v0,0x3fff
        ori $v1,$v0,0x3fff
        lui $v0,0x7000
        sw $v1,0x113c($v0)
        lui $v0,0x7000
        lw $v0,0x1114($v0)
        lh $v1,0x138($v0)
        lui $v0,0x7000
        sh $v1,0x1124($v0)
        lui $v0,0x7000
        lh $v0,0x1124($v0)
        dsll32 $v0,$v0,0x10
        dsra32 $v0,$v0,0x10
        sll $v1,$v0,1
        lui $v0,0x5b
        addiu $v0,$v0,0x7400
        addu $v0,$v1,$v0
        lw $v0,0($v0)
        jalr $ra, $v0
        lui $v0,0xba
        ori $v1,$v0,0xc2a0
        lui $v0,0x7000
        sw $v1,0x1104($v0)
        addiu $v1,$zero,3
        lui $v0,0x7000
        sw $v1,0x1140($v0)
        jal func_00293BE0
        lui $v0,0xba
        ori $v1,$v0,0xc340
        lui $v0,0x7000
        sw $v1,0x1104($v0)
        addiu $v1,$zero,3
        lui $v0,0x7000
        sw $v1,0x1140($v0)
        jal func_00293BE0
        jal func_00293B10
    }
}


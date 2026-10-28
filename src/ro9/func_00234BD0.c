typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
extern void func_00235A30();
void func_00234BD0(void)
{
    __asm {
        jal func_00235A30
        lui $v0,0x7000
        sw $zero,0x1124($v0)
        lui $v0,0x7000
        lw $v0,0x1104($v0)
        lw $v1,0x1c($v0)
        lui $v0,0x7000
        sw $v1,0x1100($v0)
        lui $v0,0x7000
        lw $v0,0x1100($v0)
        lb $v1,0xd($v0)
        lui $v0,0x7000
        sb $v1,0x1124($v0)
        lui $v0,0x7000
        lh $v1,0x1124($v0)
        lui $v0,0x7000
        lh $v0,0x1124($v0)
        addu $v1,$v1,$v0
        lui $v0,0x7000
        sh $v1,0x1124($v0)
        lui $v0,0x7000
        lh $v1,0x1124($v0)
        lui $v0,0x7000
        sh $v1,0x1128($v0)
        lui $v0,0x7000
        lh $v0,0x1128($v0)
        dsll32 $v0,$v0,0x10
        dsra32 $v0,$v0,0x10
        sll $v1,$v0,1
        lui $v0,0x5b
        addiu $v0,$v0,0x4c90
        addu $v0,$v1,$v0
        lw $v0,0($v0)
        jalr $ra, $v0
    }
}


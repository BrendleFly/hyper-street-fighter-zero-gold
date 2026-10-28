typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
void func_0057BB10(void)
{
    __asm {
        addiu $v1,$zero,1
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sb $v1,1($v0)
        lui $v0,0x7000
        sw $zero,0x1124($v0)
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        lb $v1,8($v0)
        lui $v0,0x7000
        sb $v1,0x1124($v0)
        lui $v0,0x7000
        lh $v0,0x1124($v0)
        addiu $v1,$v0,-8
        lui $v0,0x7000
        sh $v1,0x1124($v0)
        lui $v0,0x7000
        lbu $v0,0x1124($v0)
        srl $v1,$v0,1
        lui $v0,0x7000
        sb $v1,0x1124($v0)
        lui $v0,0x7000
        lh $v1,0x1124($v0)
        lui $v0,0x7000
        sh $v1,0x1128($v0)
        lui $v0,0x7000
        lh $v0,0x1128($v0)
        dsll32 $v0,$v0,0x10
        dsra32 $v0,$v0,0x10
        sll $v1,$v0,1
        lui $v0,0x5d
        addiu $v0,$v0,-0x5060
        addu $v0,$v1,$v0
        lw $v0,0($v0)
        jalr $ra, $v0
    }
}


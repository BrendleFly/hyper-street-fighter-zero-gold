typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
void func_00542270(void)
{
    __asm {
        lui $v0,0x7000
        lw $v1,0x1118($v0)
        lb $v0,4($v1)
        addiu $v0,$v0,2
        sb $v0,4($v1)
        addiu $v1,$zero,1
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sb $v1,0x30($v0)
        addiu $v1,$zero,2
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sb $v1,9($v0)
        lui $v0,0x7000
        lw $v0,0x1110($v0)
        lb $v1,0x102($v0)
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sb $v1,0x5f($v0)
        lui $v0,0x7000
        lw $v0,0x1110($v0)
        lw $v1,0x18($v0)
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sw $v1,0x18($v0)
        lui $v0,0x7000
        lw $v0,0x1110($v0)
        lh $v1,0xc($v0)
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sh $v1,0xc($v0)
        lui $v0,0x7000
        lw $v0,0x1110($v0)
        lb $v1,0xe($v0)
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sb $v1,0xe($v0)
        lui $v0,0x7000
        lw $v0,0x1110($v0)
        lb $v1,0xb($v0)
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sb $v1,0xb($v0)
        lui $v0,0x7000
        lw $v0,0x1110($v0)
        lh $v1,0x26($v0)
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sh $v1,0x26($v0)
        lui $v0,0x7000
        lw $v0,0x1110($v0)
        lh $v1,0x12($v0)
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sh $v1,0x12($v0)
        lui $v0,0x7000
        lw $v0,0x1110($v0)
        lh $v1,0x16($v0)
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        sh $v1,0x16($v0)
        lui $v0,0x7000
        sw $zero,0x1124($v0)
        lui $v0,0x7000
        lw $v0,0x1118($v0)
        lb $v1,3($v0)
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
        addiu $v0,$v0,-0x7ab0
        addu $v0,$v1,$v0
        lw $v0,0($v0)
        jalr $ra, $v0
    }
}


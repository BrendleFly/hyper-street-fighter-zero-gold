typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
void func_00506890(void)
{
    __asm {
        lui $v0,0x7000
        lw $v0,0x1114($v0)
        lh $v1,0xc($v0)
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
        lui $v0,0x5c
        addiu $v0,$v0,0x6830
        addu $v0,$v1,$v0
        lw $v0,0($v0)
        jalr $ra, $v0
    }
}


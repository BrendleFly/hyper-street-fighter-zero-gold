typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
void func_002181B0(void)
{
    volatile u32 a;
    (void)&a;
    __asm {
        sw $a0,0x10($sp)
        lw $a0,0x10($sp)
        lw $v0,0x10($sp)
        lb $v0,2($v0)
        dsll32 $v0,$v0,0x18
        dsra32 $v0,$v0,0x18
        sll $v1,$v0,2
        lui $v0,0x5b
        addiu $v0,$v0,0x2360
        addu $v0,$v0,$v1
        lw $v0,0($v0)
        jalr $ra, $v0
    }
}


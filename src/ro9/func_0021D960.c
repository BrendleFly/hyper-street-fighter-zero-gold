typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
void func_0021D960(void)
{
    __asm {
        lui $v0,0x7000
        lw $v0,0x1114($v0)
        lh $v0,8($v0)
        dsll32 $v0,$v0,0x10
        dsra32 $v0,$v0,0x10
        sra $v0,$v0,1
        sll $v1,$v0,2
        lui $v0,0x5b
        addiu $v0,$v0,0x3f10
        addu $v0,$v0,$v1
        lw $v0,0($v0)
        jalr $ra, $v0
    }
}


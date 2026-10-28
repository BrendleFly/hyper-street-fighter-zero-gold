SECTIONS
{
  . = 0x1F0000;
  .header 0x1F0000 : { build/header.o(.rodata) }
  .text  0x1F0080 : { *(.text) }
  .data  0x5AF580 : { build/data.o(.data) }
  /DISCARD/ : { *(*) }
}

#ifndef SFZFG_COMMON_H
#define SFZFG_COMMON_H

typedef unsigned char  u8;
typedef unsigned short u16;
typedef unsigned int   u32;
typedef signed   char  s8;
typedef signed   short s16;
typedef signed   int   s32;

/* EE scratchpad page — the game's hot work area (16 KB at 0x70000000).
   Code materializes this base with `lui v1, 0x7000` and addresses fields
   by offset; the matched idiom is an int temp for the base. */
#define SCRATCH_BASE 0x70000000

#endif

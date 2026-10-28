# Hyper Street Fighter Zero Gold

Reverse-engineering the hidden game **Hyper Street Fighter Zero** that ships inside the PlayStation 2 disc *Street Fighter Zero: Fighter's Generation* (Japan). I might stop there, since I'm pretty sure there's already better ways to play the rest of the games that are in this compilation. Just for fun, I've added 'Gold' to my version, since it's tradition to have confusing names when it comes to Street Fighter.

## What's in here

| Folder | Description |
|---|---|
| `src/ro9/` | The game's logic, rewritten in C. One file per function |
| `tools/roundtrip/` | The tooling that compiles the C, links a full game image, and proves it byte-identical |

## Information

- As far as I know, Hyper Street Fighter Zero has only ever been released in the compilation called *Street Fighter Zero: Fighter's Generation*. It can be played on a PS2 emulator, but I figured it might be interesting to build a native PC version.
  
- If I can get it working, I'll later look into adding a way to play it online against other people.

## Status & roadmap

Done so far: about 29% of the game, full-image verified byte-exact. Remaining: the rest of the function pool, then a hardware-abstraction layer to run it natively on a PC. Testing on only Windows 11 for now, but I want to look into Linux later (especially Batocera).

## Legal note

This repository contains **no game code, art, music, or data** from the original disc — only newly written C code and tools. To build or use it, you must own the original game disc and extract the data from it yourself. If I have time later, I'll explain how to do this, or link to a guide.

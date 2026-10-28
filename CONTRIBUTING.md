# Contributing

Want to help decompile Hyper Street Fighter Alpha? Great — here's how
it works, in three steps:

1. **Pick a function.** `src/ro9/matched.txt` lists everything already
   done; anything in the game but not in that file is fair game.
   Comment on an issue or open one to claim it (avoids duplicate work).
2. **Write the C.** Recreate the function in C until your compiler
   output matches the original machine code, instruction for
   instruction. The files in `src/ro9/` are full of worked examples.
3. **Open a pull request.** The one rule: the complete game must still
   rebuild **byte-exact** with your function included. That check is
   objective and automatic — if the bytes match, your contribution is
   correct.

Other help that matters: better tooling, documentation, and play-side
knowledge (what each routine *does* in game terms — moves, timers,
hitboxes). See the README for the big picture.

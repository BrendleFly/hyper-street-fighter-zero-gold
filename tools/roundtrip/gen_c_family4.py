#!/usr/bin/env python3
"""gen v4: if/else support + absolute globals + compound RMW.

New over gen_c_family3.py:
  * conditional branches (forward-only, if-without-else, no nesting in v1)
    - beqz/bnez/bgez/bltz/blez/bgtz load-tests
    - andi mask-tests         (if (x & K))
    - slt/sltu/slti compares  (if (a < b))
  * absolute global addresses: lui + load/store-with-offset and
    lui+addiu+load both modelled as ("ABS", addr)
  * compound read-modify-write stores recognised:
      lb t, o(p); ori t, t, K; sb t, o(p)   ->  *q = *q | K;
    (the byte-exact form from the 2026-10-22 pilot: a temp-variable RMW
    emits an extra `move` and does NOT match)
  * functions containing dsll/dsra widening or $sp frames are skipped
    (separate walls, see HANDOFF section 9)
  * every rejection is counted so the next extension is data-driven

Usage: python3 gen_c_family4.py [max_functions] [start_index] [max_bytes]
Writes pilots/spec_gen4.txt, tests it with tryc_fast2.py, prints WIN lines.
"""
import collections
import glob
import os
import re
import subprocess
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS64, CS_MODE_LITTLE_ENDIAN

ROOT = "/home/user/sfzfg/roundtrip"
SPEC = f"{ROOT}/pilots/spec_gen4.txt"
HARNESS = f"{ROOT}/pilots/tryc_fast2.py"
img = open(f"{ROOT}/ro9_original.bin", "rb").read()
md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS64 + CS_MODE_LITTLE_ENDIAN)

REG = {1: "at", 2: "v0", 3: "v1", 4: "a0", 5: "a1", 6: "a2", 7: "a3",
       8: "t0", 9: "t1", 10: "t2", 11: "t3", 12: "t4", 13: "t5", 14: "t6", 15: "t7",
       16: "s0", 17: "s1", 18: "s2", 19: "s3", 20: "s4", 21: "s5", 22: "s6", 23: "s7",
       24: "t8", 25: "t9", 28: "gp", 29: "sp", 30: "fp", 31: "ra"}

COMPILERS = ["3.0.1b210", "3.0b52", "2.4"]
LOAD_TYPES = {"lb": "s8", "lbu": "u8", "lh": "s16", "lhu": "u16", "lw": "u32"}
STORE_TYPES = {"sb": "u8", "sh": "u16", "sw": "u32"}
BRANCH_OPS = {"beqz", "bnez", "bgez", "bltz", "blez", "bgtz"}
WIDEN = {"dsll", "dsra", "dsrl", "dsll32", "dsra32", "dsrl32"}
MMI = ("addu.qb", "subu.qb", "xori.b", "aver_u.h", "aver_s.h",
       "aver_u.w", "aver_s.w", "pand", "por", "pxor", "pexc")

REJECT = collections.Counter()

TYPEDEFS = """typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;
"""


class Stop(Exception):
    pass


def rname(tok):
    if tok == "zero":
        return 0
    for n, s in REG.items():
        if s == tok:
            return n
    return None


def toks_of(ins):
    raw = ins.op_str.replace(",", " ").split()
    out = []
    for p in raw:
        if p.startswith("$"):
            out.append(("r", p[1:]))
        elif "(" in p:
            off, _, reg = p.partition("(")
            try:
                o = int(off, 0) if off else 0
            except ValueError:
                raise Stop("bad-disp")
            out.append(("m", o, reg.rstrip(")").lstrip("$")))
        else:
            out.append(("i", p))
    return out


def s16(v):
    if v > 0xFFFF:
        v -= 0x100000000
    if v >= 0x8000:
        v -= 0x10000
    return v


# ---------------------------------------------------------------- straight-line

def decode_run(insns, env=None, nc=None):
    """Decode straight-line code into (acts, env).

    env/nc may be supplied so a region continues the definitions of the
    enclosing straight-line code (values that live across a branch), and so
    decoded value names stay globally unique within a function.
    """
    if env is None:
        env = {}
    if nc is None:
        nc = [0]
    acts = []

    def newname():
        nc[0] += 1
        return "v%d" % nc[0]

    for ins in insns:
        m = ins.mnemonic
        t = toks_of(ins)

        if m in ("jr", "nop"):
            continue
        if m in MMI:
            continue
        if m == "ext" and len(t) == 4 and t[3][0] == "i" and int(t[3][1], 0) == 1:
            continue
        if m == "lui":
            dst = rname(t[0][1])
            imm = int(t[1][1], 0)
            env[dst] = ("base",) if imm == 0x7000 else ("hi", imm)
            continue
        if m in ("addiu", "ori", "xori"):
            dst = rname(t[0][1])
            src = rname(t[1][1]) if t[1][0] == "r" else None
            if src == 0:
                src = None
            imm = s16(int(t[2][1], 0)) if m == "addiu" else int(t[2][1], 0) & 0xFFFF
            if src is not None and env.get(src, ("?",))[0] == "hi":
                hi = env[src][1]
                if m == "addiu":
                    env[dst] = ("const", (hi << 16) + imm)
                    continue
                if m == "ori":
                    env[dst] = ("const", (hi << 16) | imm)
                    continue
                raise Stop("xori-hi")
            if src is None:
                env[dst] = ("const", imm)
                continue
            e = env.get(src)
            if e is None:
                raise Stop("cold-reg:" + m)
            if e[0] == "const":
                if m == "addiu":
                    env[dst] = ("const", e[1] + imm)
                elif m == "ori":
                    env[dst] = ("const", e[1] | imm)
                else:
                    env[dst] = ("const", e[1] ^ imm)
                continue
            if e[0] == "base":
                env[dst] = ("ptr", imm)
                continue
            if e[0] == "ptr":
                raise Stop("ptr-chain-addiu")
            if e[0] == "val":
                env[dst] = ("val", e[1], "%s %s %d" % (e[2], {"addiu": "+", "ori": "|", "xori": "^"}[m], imm), e[3])
                continue
            raise Stop("addiu-src:" + e[0])
        if m in ("add", "addu", "sub", "subu", "and", "andi", "or", "xor",
                 "nor", "sll", "srl", "sra", "slt", "sltu", "slti", "sltiu",
                 "not", "neg", "negu"):
            dst = rname(t[0][1])
            src = rname(t[1][1]) if t[1][0] == "r" else None
            if src == 0:
                src = None
            imm = None
            if len(t) == 3 and t[2][0] == "i":
                imm = int(t[2][1], 0)
                if m not in ("andi", "slti", "sltiu") and imm >= 0x8000:
                    imm -= 0x10000
            e = env.get(src) if src is not None else None
            if e is None:
                raise Stop("cold-reg:" + m)
            if e[0] == "const" and imm is not None:
                v = e[1]
                if m in ("add", "addu"):
                    v += imm
                elif m in ("sub", "subu"):
                    v -= imm
                elif m in ("and", "andi"):
                    v &= imm
                elif m == "or":
                    v |= imm
                elif m == "xor":
                    v ^= imm
                elif m == "sll":
                    v <<= imm
                elif m in ("srl", "sra"):
                    v >>= imm
                elif m in ("slt", "slti"):
                    v = 1 if v < imm else 0
                elif m in ("sltu", "sltiu"):
                    v = 1 if (v & 0xFFFFFFFF) < (imm & 0xFFFFFFFF) else 0
                else:
                    raise Stop("const-op:" + m)
                env[dst] = ("const", v)
                continue
            if e[0] == "val":
                ctype, cexpr = e[1], e[2]
                if imm is not None and m in ("add", "addu", "sub", "subu", "and", "andi", "or", "xor"):
                    sym = {"add": "+", "addu": "+", "sub": "-", "subu": "-",
                           "and": "&", "andi": "&", "or": "|", "xor": "^"}[m]
                    env[dst] = ("val", ctype, "(%s %s %d)" % (cexpr, sym, imm), ctype)
                    continue
                # reg-reg ALU on two known values
                if imm is None and len(t) == 3 and t[2][0] == "r":
                    src2 = rname(t[2][1])
                    if src2 == 0:
                        env[dst] = ("val", ctype, "(%s %s 0)" % (cexpr, {"add": "+", "addu": "+", "or": "|", "xor": "^", "and": "&"}.get(m, "+")), ctype)
                        continue
                    e2 = env.get(src2)
                    if e2 is not None and e2[0] in ("val", "const"):
                        rhs = e2[2] if e2[0] == "val" else str(e2[1])
                        if m in ("slt", "sltu"):
                            env[dst] = ("val", "u32", "(%s < %s)" % (cexpr, rhs), "u32")
                            continue
                        sym = {"add": "+", "addu": "+", "sub": "-", "subu": "-",
                               "and": "&", "or": "|", "xor": "^", "nor": "~"}.get(m)
                        if sym is None:
                            raise Stop("alu-rr:" + m)
                        env[dst] = ("val", ctype, "(%s %s %s)" % (cexpr, sym, rhs), ctype)
                        continue
                    raise Stop("alu-rr-cold:" + m)
                if imm is not None and m in ("slt", "slti", "sltu", "sltiu"):
                    env[dst] = ("val", "u32", "(%s < %d)" % (cexpr, imm), "u32")
                    continue
                if imm is not None and m in ("sll", "srl", "sra"):
                    sym = {"sll": "<<", "srl": ">>", "sra": ">>"}[m]
                    env[dst] = ("val", ctype, "(%s %s %d)" % (cexpr, sym, imm), ctype)
                    continue
                if m in ("not", "neg", "negu"):
                    expr = "(~%s)" % cexpr if m == "not" else "(-%s)" % cexpr
                    env[dst] = ("val", ctype, expr, ctype)
                    continue
            raise Stop("alu:" + m)
        if m == "move":
            dst = rname(t[0][1])
            src = rname(t[1][1])
            if src == 0:
                env[dst] = ("const", 0)
            elif src in env:
                env[dst] = env[src]
            else:
                raise Stop("move-cold")
            continue
        if m in LOAD_TYPES:
            dst = rname(t[0][1])
            if t[1][0] != "m":
                raise Stop("load-form")
            off, br = t[1][1], rname(t[1][2])
            e = env.get(br)
            if e is None:
                raise Stop("load-cold-base")
            ctype = LOAD_TYPES[m]
            if e[0] == "base":
                target = ("BASE", off)
            elif e[0] == "hi":
                target = ("ABS", (e[1] << 16) + s16(off))
            elif e[0] == "const":
                target = ("ABS", e[1] + off)
            elif e[0] == "ptr":
                target = ("BASE", e[1] + off)
            elif e[0] == "val" and e[1] == "u32":
                target = ("VALUE", e[2], off)
            else:
                raise Stop("load-base:" + e[0])
            name = newname()
            acts.append(("load", name, ctype, target))
            env[dst] = ("val", ctype, name, ctype)
            continue
        if m in STORE_TYPES:
            src = rname(t[0][1])
            if t[1][0] != "m":
                raise Stop("store-form")
            off, br = t[1][1], rname(t[1][2])
            e = env.get(br)
            if e is None:
                raise Stop("store-cold-base")
            ctype = STORE_TYPES[m]
            if e[0] == "base":
                target = ("BASE", off)
            elif e[0] == "hi":
                target = ("ABS", (e[1] << 16) + s16(off))
            elif e[0] == "const":
                target = ("ABS", e[1] + off)
            elif e[0] == "ptr":
                target = ("BASE", e[1] + off)
            elif e[0] == "val" and e[1] == "u32":
                target = ("VALUE", e[2], off)
            else:
                raise Stop("store-base:" + e[0])
            se = env.get(src)
            if se is None and src == 0:
                val = ("CONST", 0)                     # sw $zero, off($reg)
            elif se is None:
                raise Stop("store-cold-val")
            elif se[0] == "const":
                val = ("CONST", se[1])
            elif se[0] == "hi":
                # storing a bare lui result: a constant with zero low half
                val = ("CONST", se[1] << 16)
            elif se[0] == "val":
                val = ("VAR", se[2], se[1])
            else:
                raise Stop("store-val:" + se[0])
            acts.append(("store", ctype, target, val))
            continue
        if m == "jal":
            acts.append(("call", int(ins.op_str, 0)))
            continue
        if m == "jalr":
            if not t or t[0][0] != "r":
                raise Stop("jalr-form")
            e = env.get(rname(t[0][1]))
            if e is None or e[0] != "const":
                raise Stop("jalr-nonconst")
            acts.append(("fpcall", e[1]))
            continue
        raise Stop("insn:" + m)

    # compound RMW post-pass:  load v from T ... store (v OP K) to T
    # NB: addiu/ori/xori build "v4 | 8" (no parens); ALU ops build "(v4 | 8)".
    out = []
    i = 0
    while i < len(acts):
        a = acts[i]
        if a[0] == "load":
            name, ct, target = a[1], a[2], a[3]
            rx = re.compile(r"^\(?%s ([|&^+-]) (-?\d+)\)?$" % re.escape(name))
            for j in range(i + 1, len(acts)):
                b = acts[j]
                if b[0] == "store" and b[2] == target and b[3][0] == "VAR" and \
                        rx.match(b[3][1]):
                    clash = any(
                        (x[0] in ("load", "store") and x[2] == target) or
                        (x[0] == "store" and x[3][0] == "VAR" and name in x[3][1])
                        for x in acts[i + 1:j])
                    if not clash:
                        mm = rx.match(b[3][1])
                        out.append(("rmw", ct, target, mm.group(1), int(mm.group(2))))
                        i = j + 1
                        break
            else:
                out.append(a)
                i += 1
                continue
            continue
        out.append(a)
        i += 1
    return out, env


# ---------------------------------------------------------------- structuring

def branch_target(ins):
    toks = ins.op_str.replace(",", " ").split()
    try:
        return int(toks[-1], 0)
    except ValueError:
        return None


def structure(insns, va, size):
    """Split a function into segments:
       ("acts", acts) | ("if", cond, [nested segments])
       v2: then-blocks may themselves contain forward conditional branches
       (nested if), recursively.  No else, no loops, no early return.
    """
    end = va + size
    # find the terminating jr $ra; everything after must be nop
    jr_idx = None
    for k, x in enumerate(insns):
        if x.mnemonic == "jr":
            if "$ra" not in x.op_str:
                raise Stop("jr-non-ra")
            jr_idx = k
            break
    if jr_idx is None:
        raise Stop("no-jr")
    if any(x.mnemonic != "nop" for x in insns[jr_idx + 1:]):
        raise Stop("code-after-jr")
    body = insns[:jr_idx]
    alias = {}
    segs, _ = structure_region(body, va, end, {}, [0], alias)
    return segs, alias



def structure_region(insns, va_lo, va_hi, env, nc, alias):
    """Segments: ("acts", acts) | ("if", cond, then_segs, else_segs_or_None).
    A branch may target the region END (== va_hi): jump-to-join.

    env/nc (the value environment and the name counter) are threaded through
    the region so that a value defined before a branch is visible inside its
    arms; each arm receives a copy of the environment but shares the name
    counter, so decoded names stay unique within the function.

    At the join, a register defined inside an arm is merged back into the
    environment, because the original keeps that register's value across the
    join.  When the register already held a value before the branch, the
    arm's value is aliased onto the earlier one so the C reads
    `x = ...; if (c) { x = ...; } ... use x;`."""
    segs = []
    run_start = 0
    i = 0
    n = len(insns)
    addrs = [x.address for x in insns]

    def idx_of(addr):
        """Index of the first decoded instruction at-or-after `addr`
        (capstone silently drops MMI marker words, so an exact-address
        search fails when the target lands on one).  n == region end."""
        import bisect
        return bisect.bisect_left(addrs, addr)

    while i < n:
        ins = insns[i]
        if ins.mnemonic in BRANCH_OPS:
            REJECT["branch-seen"] += 1
            if i + 1 >= n or insns[i + 1].mnemonic != "nop":
                raise Stop("delay-slot")
            tgt = branch_target(ins)
            if tgt is None or not (va_lo <= tgt <= va_hi):
                raise Stop("branch-target-out")
            if tgt <= ins.address:
                raise Stop("backward-branch")
            tidx = idx_of(tgt)
            if tidx >= n and tgt != va_hi:
                raise Stop("branch-target-miss")
            if tidx <= i + 1:
                tidx = i + 2 if tgt > ins.address else tidx
            then = insns[i + 2:tidx]
            # else detection FIRST (strips the trailing `b J; nop`), then the
            # control-transfer check on what remains of the then-block
            else_segs = None
            else_env = None
            join_idx = tidx
            if (len(then) >= 2 and then[-2].mnemonic == "b"
                    and then[-1].mnemonic == "nop"):
                try:
                    j = int(then[-2].op_str, 0)
                except ValueError:
                    j = None
                if j is not None and tidx < j <= va_hi:
                    jidx = idx_of(j)
                    if jidx > n:
                        jidx = n
                    if jidx <= tidx:
                        raise Stop("else-join-miss")
                    else_insns = insns[tidx:jidx]
                    for x in else_insns:
                        if x.mnemonic in ("j", "b", "jr"):
                            raise Stop("else-control-transfer")
                    else_segs = ("pending", else_insns, tgt, j)
                    then = then[:-2]
                    join_idx = jidx
            for x in then:
                if x.mnemonic in ("j", "b", "jr"):
                    raise Stop("then-control-transfer")
            if i == run_start:
                raise Stop("branch-without-run")
            # the producer (last insn before the branch) is decoded as part
            # of the run: for load-tests its load act must render as a
            # statement, and its env entry identifies the tested variable.
            run = insns[run_start:i]
            producer = insns[i - 1]
            acts, env = decode_run(run, env, nc)
            cond = extract_cond(producer, ins, env, acts)
            # the else arm is decoded after the run, so it sees the values
            # defined before the branch
            if else_segs is not None and else_segs[0] == "pending":
                _, else_insns, elo, ehi = else_segs
                else_segs, else_env = structure_region(
                    else_insns, elo, ehi, dict(env), nc, alias)
                if not else_segs or all(s == ("acts", []) for s in else_segs):
                    raise Stop("empty-else")
            then_lo = then[0].address if then else ins.address
            then_segs, then_env = structure_region(
                then, then_lo, tgt, dict(env), nc, alias)
            # merge the arm's definitions back at the join
            if else_segs is None:
                for r, e in then_env.items():
                    if e[0] != "val":
                        continue
                    if r in env and env[r][0] == "val":
                        alias[e[2]] = env[r][2]        # reuse the earlier var
                    elif r not in env:
                        env[r] = e
            else:
                for r, e in then_env.items():
                    if e[0] != "val" or r in env:
                        continue
                    if r in else_env and else_env[r] == e:
                        env[r] = e
            if not then_segs or all(s == ("acts", []) for s in then_segs):
                raise Stop("empty-then")
            segs.append(("acts", acts))
            segs.append(("if", cond, then_segs, else_segs))
            run_start = join_idx
            i = join_idx
            continue
        if ins.mnemonic in ("j", "b"):
            raise Stop("uncond-jump")
        i += 1
    tail = insns[run_start:i]
    tacts, env = decode_run(tail, env, nc)
    segs.append(("acts", tacts))
    return segs, env


def extract_cond(producer, branch, env, run_acts):
    """Turn (producer insn, branch insn) into a condition descriptor."""
    pm = producer.mnemonic
    b = branch.mnemonic
    val_of = lambda e: e[2] if e and e[0] == "val" else None
    if pm in LOAD_TYPES:
        t = toks_of(producer)
        dst = rname(t[0][1])
        e = env.get(dst)
        name = val_of(e)
        if name is None:
            raise Stop("cond-load-env")
        ct = e[1]
        opmap = {"beqz": ("bool", False), "bnez": ("bool", True),
                 "bgez": ("lt0", False), "bltz": ("ge0", False),
                 "blez": ("gt0", False), "bgtz": ("le0", False)}
        kind, _ = opmap[b]
        return ("loadtest", name, ct, kind)
    if pm == "andi":
        t = toks_of(producer)
        dst = rname(t[0][1])
        e = env.get(dst)
        if e is None or e[0] != "val" or not e[2].startswith("(") or " & " not in e[2]:
            raise Stop("cond-andi-env")
        name = e[2][1:e[2].index(" & ")]
        k = int(e[2][e[2].index(" & ") + 3:-1])
        return ("masktest", name, k, b == "bnez")
    if pm in ("slt", "sltu", "slti", "sltiu"):
        t = toks_of(producer)
        dst = rname(t[0][1])
        e = env.get(dst)
        if e is None or e[0] != "val" or "(" not in e[2] or " < " not in e[2]:
            raise Stop("cond-slt-env")
        inner = e[2][1:-1]
        a, _, bb = inner.partition(" < ")
        return ("cmptest", a.strip(), bb.strip(), pm in ("slt", "slti"), b == "bnez")
    raise Stop("cond-producer:" + pm)


# ---------------------------------------------------------------- rendering

def render(acts, indent, chainvar_state):
    """Render acts to (decls, stmts).  chainvar_state: dict for reuse."""
    decls = []
    stmts = []
    ctr = chainvar_state

    def newvar(p):
        ctr[p] = ctr.get(p, 0) + 1
        return "%s%d" % (p, ctr[p])

    def base_assign():
        stmts.append("    " * indent + "a = 0x70000000;")

    def addr_of(target):
        if target[0] == "BASE":
            base_assign()
            return "(a + %d)" % target[1]
        if target[0] == "ABS":
            return "0x%X" % (target[1] & 0xFFFFFFFF)
        if target[0] == "VALUE":
            nm = target[1]
            if re.fullmatch(r"v\d+", nm):
                vv = ctr.get("name:" + nm)
                if vv is None:
                    raise Stop("addr-var-miss")
                base = vv
            else:
                # derived pointer (e.g. "v1 + 32"): materialise a variable so
                # MWCC emits addiu q, v, K and accesses through q
                base = ctr.get("ptr:" + nm)
                if base is None:
                    base = newvar("q")
                    decls.append("    u32 %s;" % base)
                    stmts.append("    " * indent + "%s = %s;" % (base, expr_text(nm)))
                    ctr["ptr:" + nm] = base
            off = target[2]
            if off < 0:
                return "(%s - %d)" % (base, -off)
            if off == 0:
                return "(%s)" % base
            return "(%s + %d)" % (base, off)
        raise Stop("render-target:" + str(target[0]))

    def value_var(name, ct):
        """The C variable that holds decoded value `name` (loads only)."""
        vv = ctr.get("name:" + name)
        return vv

    def expr_text(e):
        """Translate a decoded value expression to C, mapping v-names."""
        def sub(mo):
            vv = ctr.get("name:" + mo.group(0))
            if vv is None:
                raise Stop("render-expr-miss")
            return vv
        return re.sub(r"\b(v\d+)\b", sub, e)

    for act in acts:
        if act[0] == "call":
            stmts.append("    " * indent + "func_%08X();" % act[1])
            continue
        if act[0] == "fpcall":
            stmts.append("    " * indent + "((void (*)(void))func_%08X)();" % act[1])
            continue
        if act[0] == "load":
            _, name, ctype, target = act
            ali = ctr.get("alias", {}).get(name)
            vv = None
            if ali:
                # the value was also live before the branch: reuse that C
                # variable so the arm overwrites it (x = ...; if (c) x = ...).
                # If the earlier load was inlined away (nested condition), the
                # value only exists on the arm path: fresh variable is right.
                vv = ctr.get("name:" + ali)
            if vv is not None:
                ctr["name:" + name] = vv
            else:
                vv = newvar("v")
                ctr["name:" + name] = vv
                vt = ctr.get("vt:" + name) or ("s32" if ctype in ("s8", "s16") else "u32")
                decls.append("    " * 1 + "%s %s;" % (vt, vv))
            stmts.append("    " * indent + "%s = *(volatile %s *)%s;" % (vv, ctype, addr_of(target)))
            continue
        if act[0] == "store":
            _, ctype, target, val = act
            addr = addr_of(target)
            if val[0] == "CONST":
                if val[1] == 0:
                    # `= 0` stores as $zero directly (sh $zero, off($r))
                    rhs = "0"
                    vv = None
                else:
                    vv = newvar("v")
                    decls.append("    u32 %s;" % vv)
                    stmts.append("    " * indent + "%s = %d;" % (vv, val[1]))
                    rhs = vv
            else:
                rhs = value_var(val[1], val[2])
                if rhs is None:
                    try:
                        rhs = expr_text(val[1])
                    except Stop:
                        raise Stop("render-val-miss")
                vv = None
            stmts.append("    " * indent + "*(volatile %s *)%s = %s;" % (ctype, addr, rhs))
            continue
        if act[0] == "rmw":
            _, ctype, target, op, k = act
            addr = addr_of(target)
            stmts.append("    " * indent + "*(volatile %s *)%s = *(volatile %s *)%s %s %d;"
                         % (ctype, addr, ctype, addr, op, k))
            continue
        raise Stop("render-act:" + act[0])
    return decls, stmts


def build_source(va, segs, style, alias=None):
    """style: {"cond": "var"|"nested"}"""
    decls = []
    stmts = []
    ctr = {"alias": alias or {}}

    def emit_acts(acts, indent):
        d, s = render(acts, indent, ctr)
        decls.extend(d)
        stmts.extend(s)

    def find_load_act(acts, name):
        for a in acts:
            if a[0] == "load" and a[1] == name:
                return a
        return None

    def nested_load_expr(target, ctype, acts, indent):
        """Render a load with its pointer chain inlined (forces MWCC to keep
        the chain in v0/v1 expression temporaries, like the original)."""
        if target[0] == "BASE":
            stmts.append("    " * indent + "a = 0x70000000;")
            return "*(volatile %s *)(a + %d)" % (ctype, target[1])
        if target[0] == "ABS":
            return "*(volatile %s *)0x%X" % (ctype, target[1] & 0xFFFFFFFF)
        if target[0] == "VALUE":
            inner_act = find_load_act(acts, target[1])
            if inner_act is None:
                raise Stop("nested-chain-miss")
            inner = nested_load_expr(inner_act[3], inner_act[2], acts, indent)
            off = target[2]
            sep = "- %d" % (-off) if off < 0 else "+ %d" % off
            return "*(volatile %s *)(%s %s)" % (ctype, inner, sep)
        raise Stop("nested-target:" + str(target[0]))

    def cond_text(cond, indent):
        """May append decls/pre-stmts; returns the if (...) text."""
        if cond[0] == "loadtest":
            _, name, ct, kind = cond
            vv = ctr.get("name:" + name)
            if vv is None:
                raise Stop("cond-var-miss")
            forms = {"bool": "%s", "lt0": "%s < 0", "ge0": "%s >= 0",
                     "gt0": "%s > 0", "le0": "%s <= 0"}
            return forms[kind] % vv
        if cond[0] == "masktest":
            _, name, k, neg = cond
            vv = ctr.get("name:" + name)
            if vv is None:
                raise Stop("cond-var-miss")
            e = "(%s & %d)" % (vv, k) if k > 1 else "(%s & 1)" % vv
            return ("!(%s)" % e) if neg else e
        if cond[0] == "cmptest":
            _, a, b, signed, neg = cond
            def operand(x):
                if x.startswith("v") and ctr.get("name:" + x):
                    return ctr["name:" + x]
                try:
                    int(x, 0)
                    return x
                except ValueError:
                    raise Stop("cmp-operand")
            e = "(%s < %s)" % (operand(a), operand(b))
            return ("!(%s)" % e) if neg else e
        raise Stop("cond-kind")

    def newvar(p):
        ctr[p] = ctr.get(p, 0) + 1
        return "%s%d" % (p, ctr[p])

    def refs_in(seg):
        """Names referenced by a segment (acts or if), recursing into nested
        if-segments.  A popped producer stashed in seg[3] is deliberately NOT
        counted — its chain load was inlined away."""
        out = set()
        if seg[0] == "if":
            c = seg[1]
            if c[0] in ("loadtest", "masktest"):
                out.add(c[1])
            elif c[0] == "cmptest":
                for x in (c[1], c[2]):
                    if re.fullmatch(r"v\d+", x):
                        out.add(x)
            for sub in list(seg[2]) + list(seg[3] or []):
                out |= refs_in(sub)
            return out
        for a in seg[1]:
            if a[0] == "load":
                t = a[3]
                if t[0] == "VALUE":
                    out.add(t[1])
            elif a[0] in ("store", "rmw"):
                t = a[2]
                if t[0] == "VALUE":
                    out.add(t[1])
                if a[0] == "store" and a[3][0] == "VAR":
                    out.update(re.findall(r"\bv\d+\b", a[3][1]))
        return out

    def emit_segments(segments, indent):
        segs2 = [list(seg) for seg in segments]
        nested_on = style.get("cond") == "nested"
        popped_map = {}
        for k, seg in enumerate(segs2):
            if seg[0] != "if" or seg[1][0] != "loadtest" or not nested_on:
                continue
            cond = seg[1]
            prev = segs2[k - 1] if k > 0 else None
            if not (prev and prev[0] == "acts" and prev[1]
                    and prev[1][-1][0] == "load" and prev[1][-1][1] == cond[1]):
                continue
            popped_map[id(seg)] = prev[1].pop()
            # chain loads left dead by the inlining are dropped (fixpoint)
            changed = True
            while changed:
                allrefs = set()
                for s2 in segs2:
                    allrefs |= refs_in(s2)
                changed = False
                for k2 in range(len(prev[1]) - 1, -1, -1):
                    a = prev[1][k2]
                    if a[0] == "load" and a[1] not in allrefs:
                        prev[1].pop(k2)
                        changed = True
                        break
        flat = []
        for seg in segs2:
            if seg[0] == "acts":
                emit_acts(seg[1], indent)
                flat.extend(seg[1])
                continue
            _, cond, then_segs, else_segs = seg
            if id(seg) in popped_map:
                _, name, ct, target = popped_map[id(seg)]
                cn = newvar("v")
                ctr["name:" + name] = cn
                vt = ctr.get("vt:" + name) or ("s32" if ct in ("s8", "s16") else "u32")
                decls.append("    %s %s;" % (vt, cn))
                expr = nested_load_expr(target, ct, flat, indent)
                stmts.append("    " * indent + "%s = %s;" % (cn, expr))
            ctext = cond_text(cond, indent)
            stmts.append("    " * indent + "if (%s) {" % ctext)
            emit_segments(then_segs, indent + 1)
            if else_segs is not None:
                stmts.append("    " * indent + "} else {")
                emit_segments(else_segs, indent + 1)
            stmts.append("    " * indent + "}")

    # a sign-tested u32 load must be declared s32 so `v < 0` emits bgez/bltz
    def walk(segments):
        for s in segments:
            yield s
            if s[0] == "if":
                yield from walk(s[2])
                if s[3]:
                    yield from walk(s[3])
    for seg in walk(segs):
        if seg[0] == "if":
            c = seg[1]
            if c[0] == "loadtest" and c[3] != "bool" and c[2] == "u32":
                ctr["vt:" + c[1]] = "s32"

    # the producer load for a loadtest must render BEFORE the if: it is the
    # last act of the preceding acts-segment, so plain ordering suffices.
    emit_segments(segs, 1)
    if not stmts:
        raise Stop("empty-body")
    seen = set()
    dd = []
    for d in decls:
        if d not in seen:
            seen.add(d)
            dd.append(d)
    ext = []
    eseen = set()
    for seg in walk(segs):
        if seg[0] != "acts":
            continue
        for a in seg[1]:
            if a[0] in ("call", "fpcall"):
                l = "extern void func_%08X();" % a[1]
                if l not in eseen:
                    eseen.add(l)
                    ext.append(l)
    hdr = "void func_%08X(void)" % va
    body = [hdr, "{", "    u32 a;"] + dd + stmts + ["}"]
    src = TYPEDEFS + "\n".join(ext + body) + "\n"
    if style.get("perm"):
        idx = style["perm"]
        if len(idx) != len(dd):
            raise Stop("perm-len")
        dd = [dd[i] for i in idx]
        body = [hdr, "{", "    u32 a;"] + dd + stmts + ["}"]
        src = TYPEDEFS + "\n".join(ext + body) + "\n"
    return src, len(dd)


# ---------------------------------------------------------------- main

def load_insns(stem):
    va = int(stem[5:], 16)
    n = sum(1 for l in open(f"{ROOT}/ro9/{stem}.s") if l.strip().startswith(".word"))
    off = va - 0x1F0000
    return va, n * 4, list(md.disasm(img[off:off + n * 4], va))


def strip_call_frame(insns):
    """If the ONLY stack traffic is the standard call frame
    (addiu -K; sd ra,X(sp); ...; ld ra,X(sp); addiu +K; jr ra), return the
    body without it (MWCC re-emits the frame itself), else None."""
    idx = [k for k, x in enumerate(insns) if "$sp" in x.op_str]
    if len(idx) != 4:
        return None
    p1, p2, e1, e2 = idx
    if p1 != 0 or p2 != 1 or e2 <= e1 or e1 + 1 != e2:
        return None
    t1 = insns[p1].op_str.replace(" ", "").split(",")
    t2 = insns[e2].op_str.replace(" ", "").split(",")
    if insns[p1].mnemonic != "addiu" or t1[:2] != ["$sp", "$sp"]:
        return None
    if insns[e2].mnemonic != "addiu" or t2[:2] != ["$sp", "$sp"]:
        return None
    try:
        k = int(t1[2], 0)
        k2 = int(t2[2], 0)
    except ValueError:
        return None
    if k >= 0 or k2 != -k:
        return None
    if insns[p2].mnemonic != "sd" or "$ra" not in insns[p2].op_str:
        return None
    if insns[e1].mnemonic != "ld" or "$ra" not in insns[e1].op_str:
        return None
    if insns[e1].op_str != insns[p2].op_str:
        return None
    if e2 + 1 >= len(insns) or insns[e2 + 1].mnemonic != "jr" \
            or "$ra" not in insns[e2 + 1].op_str:
        return None
    if any(x.mnemonic != "nop" for x in insns[e2 + 2:]):
        return None
    return insns[2:e1] + [insns[e2 + 1]]


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    maxbytes = int(sys.argv[3]) if len(sys.argv) > 3 else 320
    maxperms = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    from itertools import permutations
    matched = set(l.strip().split(":")[0].split("@")[0]
                  for l in open(f"{ROOT}/src_ro9/matched.txt") if l.strip())
    cands = []
    scanned = 0
    built = 0
    branchy = 0
    for s in sorted(glob.glob(f"{ROOT}/ro9/func_*.s")):
        stem = os.path.basename(s)[:-2]
        if stem in matched:
            continue
        scanned += 1
        if scanned <= start:
            continue
        try:
            va, size, insns = load_insns(stem)
        except FileNotFoundError:
            continue
        if size > maxbytes:
            continue
        if any(i.mnemonic in WIDEN for i in insns):
            REJECT["widen"] += 1
            continue
        if any("$sp" in i.op_str for i in insns):
            stripped = strip_call_frame(insns)
            if stripped is None:
                REJECT["frame"] += 1
                continue
            insns = stripped
        try:
            segs, alias = structure(insns, va, size)
        except Stop as e:
            REJECT[str(e)] += 1
            continue
        has_if = any(seg[0] == "if" for seg in segs)
        if has_if:
            branchy += 1
        ok = False
        base_src = None
        ndecls = 0
        for st in ({"cond": "var"}, {"cond": "nested"}):
            try:
                src, nd = build_source(va, segs, st, alias)
            except Stop as e:
                REJECT["render:" + str(e)] += 1
                if str(e) == "addr-var-miss":
                    REJECT["addr-miss-stem:" + stem] += 1
                continue
            ok = True
            if base_src is None:
                base_src, ndecls = src, nd
            for comp in COMPILERS:
                cands.append((va, size, comp, src))
        # declaration-order permutations: MWCC's register allocation follows
        # decl order, so permuting can fix pure register-swap misses.
        if ok and maxperms and 2 <= ndecls <= 6:
            n = 0
            for p in permutations(range(ndecls)):
                if p == tuple(range(ndecls)):
                    continue                      # identity already covered
                try:
                    psrc, _ = build_source(va, segs,
                                           {"cond": "var", "perm": p}, alias)
                except Stop:
                    continue
                cands.append((va, size, "3.0.1b210", psrc))
                n += 1
                if n >= maxperms:
                    break
            REJECT["perm-fns"] += 1
        if ok:
            built += 1
        if built >= limit:
            break
    print(f"scanned {scanned} unmatched, built {built} ({branchy} with if), "
          f"{len(cands)} candidates")
    print("rejects:", ", ".join(f"{k}={v}" for k, v in REJECT.most_common(20)))
    parts = []
    for va, sz, comp, src in cands:
        parts.append(f"VA {va:08X}\nSIZE {sz:X}\nCOMP {comp}\nEND\n{src}---\n")
    open(SPEC, "w").write("".join(parts))
    r = subprocess.run(["python3", HARNESS, SPEC], capture_output=True, text=True)
    if r.stderr.strip():
        print("HARNESS STDERR:", r.stderr[-1500:])
    wins = []
    for line in r.stdout.splitlines():
        m = re.match(r"=== cand \d+: func_([0-9A-F]{8}) \[(\S+)\] -> (.*)", line)
        if m and "MATCH" in m.group(3):
            wins.append((m.group(1), m.group(2)))
    uniq = sorted(set(wins))
    print(f"wins: {len(wins)} / {len(cands)}  ({len(uniq)} distinct functions)")
    for w in uniq:
        print("WIN func_%s comp=%s" % w)


if __name__ == "__main__":
    main()

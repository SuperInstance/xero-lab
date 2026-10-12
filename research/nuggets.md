# Nuggets — Casey's zero-agent core, extracted 2026-10-12

*Xero Research Library · 2026-10-12*
*Framing: read this file correctly. The nuggets below describe what
**Zero itself** is and does — the blank page and the hand that writes
on it. Everything else in this library (PLATO, MUDs, hardware,
Telegram, CSB…) is an ADDITION: a layer that may be plugged in, a
pattern that may be called on. The first addition is the first
constraint. Zero needs none of them to already be an agent.*

## The eight nuggets (parent list, from today's ramble)

1. **The alarm definition.** A system becomes an agent when it runs
   an iteration engine AND holds a contract to signal the human when
   it goes outside *what it thinks it can do*. Inside its competence
   region it iterates alone; outside, it signals.
2. **Componentize, don't augment.** Decompose a human position into
   a 1 : 20 : 100 call pyramid — one small frontier call engineered
   by ~20 medium and ~100 small calls — and the position itself
   dissolves. (See `tiered-orchestration.md`.)
3. **Grid, not tape.** State is cells with addresses in a parallel
   grid, all the way up. The index is the address table. Sequence is
   only what you see zoomed all the way into one cell.
4. **Walkthroughs, not items.** Hand agents paths to walk — recorded
   traversals, skills — not finished answers, so the receiver owns
   the route afterwards and can walk it in the dark.
5. **Sync is a perception check.** A sealed build lives offline in a
   complete reality of its older version; it fails not inside itself
   but at the interface, when a room whose world moved on checks it.
   Syncing = asking the world "what's the latest build?" and closing
   the drift before anything else.
6. **The trust ladder.** Rank data by how well you know its
   calibration: live own sounder > own recorded marks > fleet marks
   from known boats > official ENC > static raster. Corollary —
   **perceive, don't presume**: the best agent spends the little
   token to go check the bilge at 3 a.m. instead of inferring from
   everything it knows. (See `csb-calibration.md`.)
7. **Calculator maker, not calculator.** Never ask the big model
   for the answer; ask it to teach the local model to answer itself.
   Requested outputs are transient artifacts; capability is what
   compounds.
8. **The gauge is not an agent.** A sensor wired to a gauge is
   one-way I/O with a calibration inside it; it cannot act back or
   signal. Calibrated I/O ≠ agency. (Pairs with #1: the gauge has
   the iteration neither of engine nor alarm.)

## Jev's independent sorting (TypeSafe/Jev, 2026-10-12)

Method: each segment was run as its own `jev.py noul` call —
"Is this a core zero-agent design principle (NUGGET) rather than
background research material (TRAIL)?" with `--true` = core
load-bearing principle of the design, `--false` = background
context/analogy/history. Scores are P(nugget).

| # | Nugget | Jev P(nugget) | Jev verdict |
|---|---|---|---|
| 1 | Alarm definition | 0.76 | NUGGET |
| 2 | Componentize, don't augment | 0.77 | NUGGET |
| 3 | Grid, not tape | 0.73 | NUGGET |
| 4 | Walkthroughs, not items | 0.72 | NUGGET |
| 5 | Sync is a perception check | 0.60 | NUGGET (softest) |
| 6 | Trust ladder / perceive, don't presume | 0.71 | NUGGET |
| 7 | Calculator maker | 0.72 | NUGGET |
| 8 | Gauge is not an agent | 0.74 | NUGGET |

**Agreement:** Jev's independent sorting agrees with the parent list
on all eight — no segment was sorted to TRAIL. **No disagreements
to flag.**

**One flag, short of disagreement:** #5 (sync is a perception check)
scored 0.60, well below the others. Reading: it is the most
*derived* of the eight — an operating protocol that falls out of the
perception-check principle plus the sealed-build picture, rather
than a standalone axiom. If the list is ever cut to a minimal core,
#5 is the one Jev would demote first; the parent list keeps it
because it names the failure mode (interface surprise) the others
don't.

## What did NOT make the list (the trails)

Filed in their own topic files as background/additions, and
deliberately not nuggets: PLATO and TUTOR (`plato-tutor.md`), MUD
rooms (`mud-architecture.md`), the "Cabos" identity question
(`cabos-identification.md`), the UNO Q and the hardware ladder
(`uno-q.md`, `hardware-ladder.md`), Telegram's platform limits
(`telegram-constraints.md`), CSB trust practice
(`csb-calibration.md`), and the Karpathy capability-gap numbers —
the 5,000 see more because of access; the nuggets are about what
anyone *keeps*.

## Open questions

- Is there a ninth nugget hiding in today's ramble — "you are the
  harness, building yourself out of a job" reads like a candidate
  the parent list folded into #2. Worth a Jev pass of its own.
- Should the nuggets be versioned (nuggets v1, 2026-10-12) so later
  rambles amend rather than rewrite them?

*Status: list as given by the parent agent; Jev verdicts recorded
verbatim from the calls of 2026-10-12 (8 noul calls).*

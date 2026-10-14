# Playthrough tiles — bootstrap zero into working agents (2026-10-13 19:24 AKDT)

Casey's direction, dictated: work with the zero agent, bootstrap it
through the bootcamp into a bunch of different, totally useful
agents. Each bootstrap is preserved as a **playthrough**; the
playthroughs become **tiles** on a page. Clicking a tile plays the
build-up — fast or slow, ticking by — from blank page to working
state, almost like a template unfolding. And at the end of the
playthrough it doesn't just show the thing: **it bootstraps as it
loads into a working thing.** A gallery of these: working proofs of
concept that are more than proofs — real tools, whose whole cost
was the bootcamp engineering (his phrase; naming delegated).

## Decomposition

1. **The mechanism already exists in pieces.** zero-bootcamp's
   doctrine — *the product is the steps* — made literal: the steps
   are recorded, and replaying the steps rebuilds the product.
   The filing loop already proves the fold: state = fold(records),
   replay reproduces the state exactly (35/35, idempotent).
2. **A playthrough = a record + a player + a boot.**
   - Record: the ordered steps of one bootstrap (what was asked,
     what was added, what the state became) — the git log is the
     natural substrate.
   - Player: ticks the steps by at visitor speed (quickly or
     slowly), the state visibly accumulating — files appearing,
     counts rising, the blank page spending its potential.
   - Boot: the final step isn't a picture of the tool; the replay
     *lands* on the working tool itself, live in the page.
3. **Tiles are patches.** SPEC principle 4: patches are built to
   stand alone; the quilt emerges. Each tile stands alone (one
   agent, one playthrough, one working tool) — the gallery is the
   quilt they make by accumulation, never a framework.
4. **Labels solve themselves.** A playthrough tile can't oversell:
   its claim is its replay. The honest label for the gallery is
   the strongest one the page has — *it rebuilds itself in front
   of you; what lands is real.*
5. **Why it's more than a PoC** (his words): the output of the
   bootcamp is not a demo of a tool, it IS the tool — the same
   record that teaches is the record that boots. Teaching and
   shipping are one artifact (cf. walkthroughs-not-items: a
   walkthrough formalized = a skill; here, a playthrough
   formalized = a working agent).

## Naming (delegated: "you'll figure it out")

- The entries: **playthroughs** (his word — keep it).
- The gallery: **the Bootcamp Gallery**.
- The process (replacing "boot camp engineering"): **replay
  bootstrapping** — the record is the recipe.
- A tile's promise, in one line: *watch it build; then it's yours.*

## First tile (parent's choice, stated to Casey)

**The Filing Agent.** Reasons: its build is already a replayable
record (deposits → cascade → state is the prototype's native
shape); the end-state tool is genuinely useful to any visitor
(paste your own rambling notes, watch them file themselves); and
its correctness is checkable — the in-browser cascade must
reproduce the Python prototype's verified behavior on the same
fixture (35/35, idempotent) before the tile earns its place.

## Open questions

- Record granularity: steps as commits? as deposits? as chapters
  with sub-steps? (First tile will answer by example.)
- Does the visitor's booted instance persist (their own store in
  the browser) or reset per visit? (Local-first says persist.)
- Which agents make the best next tiles: the wave instrument
  (pre-reader → brief → tongue; fully local, measurable), the
  Patient dictation agent (the cold readers' unanimous pick),
  the alarm/gauge agent (deadband; the 3 a.m. bilge in working
  form).
- Can a playthrough be *forked* — a visitor starts from step k
  and builds their own variant? (The quilt says yes, eventually.)

# PLATO + TUTOR — the sheet, the judge, the rooms

*Xero Research Library · 2026-10-12*
*Framing: an addition layer. PLATO is a pattern library Zero may call
on — it is not a component of Zero, which is the blank page.*

## What PLATO was

PLATO (Programmed Logic for Automated Teaching Operations), begun in
1960 at the University of Illinois under Donald Bitzer, was the first
generalized computer-assisted instruction system — and, almost by
accident, the first online community. It ran for four decades; the
last production system shut down in 2006. Everything below was built
under scarcity: a central mainframe, hundreds of terminals, and a
design culture of squeezing capability out of shared compute.

Sources: https://en.wikipedia.org/wiki/PLATO_(computer_system) ·
https://www.crn.com/slide-shows/channel-programs/225400175/celebrating-50-years-of-plato

## The sheet: a coordinate grid you place things on

- The PLATO IV terminal's **plasma display** (invented 1964 by Bitzer,
  H. Gene Slottow, and Robert Willson) was a **512 × 512 addressable
  grid** of glowing points — each pixel individually settable, and
  *inherently persistent*: once lit, a point stayed lit until new
  information replaced it. The display was memory. An infrared
  touch panel overlay the same grid, so input coordinates and output
  coordinates were one space.
- **TUTOR**, the authoring language (chief designer Paul Tenczar),
  treated a lesson screen as a *sheet* on that grid: authors placed
  text and graphics at absolute coordinates or **relative to what was
  already placed** — draw here, put this under that, leave this cell
  for the student's answer. Lessons were compositions of addressed
  regions, not streams of output.
- Steal-worthy detail: because placement was relative as well as
  absolute, content could be defined in terms of its neighbours —
  the sheet was a small relational layout system decades before CSS.

Source: https://ece.illinois.edu/about/history/hall-of-fame/plasmas

## The judge: TUTOR's answer-checking

- TUTOR's judging machinery let an author declare **anticipated
  answers**: the correct response, its spelling and phrasing variants,
  synonyms, and the *expected wrong answers*, each with its own
  feedback branch.
- A student answer was matched tolerantly (keywords, substrings,
  variant spellings) rather than by exact string equality, and could
  earn **partial credit**. A misconception wasn't just scored — it
  was *recognized by name* and routed to targeted feedback.
- Read as agent design: this is a perception check that **classifies**
  instead of merely scoring. The judge is a fixed, author-written
  harness; the student's free text is the mutable input; the verdict
  (right / variant / known-misconception / unknown) decides the next
  state. Command-level detail here is summarized from secondary
  descriptions and a MiniMax synthesis pass — treat exact TUTOR
  syntax claims as UNVERIFIED.

## The rooms: PLATO's communication inventions

All 1973–74, all on PLATO:

- **Pad** (1973) — a general-purpose message board; **Notesfiles /
  PLATO Notes** (1973, David R. Woolley) — threaded, persistent,
  topic-organized discussions; direct ancestor of newsgroups and
  Lotus Notes.
- **Talkomatic** (Nov 26, 1973, Doug Brown & David R. Woolley) —
  real-time chat organized as **six rooms, five participants each**;
  every participant had a dedicated section of the screen and text
  appeared **character-by-character as typed**. The room, the
  occupant list, and the per-person slice of the sheet were one
  object.
- **Term-talk** — 1:1 instant messaging. **Monitor Mode** (1974) —
  an instructor could share/watch a student's screen: supervised
  perception of another's room.
- **Games as shared rooms**: *Empire* (c. 1974, up to 30 players),
  *Avatar* (c. 1978, a graphical multi-user dungeon) — persistent
  multi-user spaces years before "MUD" was a word.

Source: https://en.wikipedia.org/wiki/Talkomatic

## Patterns worth calling on

1. **State as an addressed sheet.** Give every element coordinates;
   let placement be relative ("under the compass reading") as well
   as absolute. The index is the address table to the sheet.
2. **Persistence is the default, not a feature.** The plasma pixel
   stayed lit; the notesfile stayed posted. Design Zero's layers so
   state remains until deliberately replaced.
3. **Judges classify, then route.** Anticipated-answer sets with
   named misconceptions, partial credit, and per-class feedback —
   a template for perception checks and deadband alarms alike.
4. **Rooms are the social primitive.** A room = bounded membership,
   its own slice of the sheet, its own persistent record. Chat,
   games, and lessons were all rooms on PLATO; the shape scales.

## Open questions

- Talkomatic's per-occupant screen slice: is that the right model
  for multi-agent rooms (each agent sees the room rendered from its
  own slice), or does it fragment shared state?
- TUTOR judging assumed an author who pre-writes the anticipated
  answers. Who writes the anticipated-answer set for a Xero judge —
  the human, or the frontier call (with the set then frozen as a
  fixed harness, AutoResearch-style)?

*Status: high confidence on PLATO/Talkomatic/Notes facts; TUTOR
judging summarized, command-level detail UNVERIFIED.*

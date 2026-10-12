# "Cabos" — identification attempt (open)

*Xero Research Library · 2026-10-12*
*Framing: an addition layer — specifically, an unidentified one.
Casey said to combine PLATO's sheet with "Cabos" (voice
transcription, word uncertain), described as an old ledger-based
system from the era of squeezing processing efficiency out of scarce
machines. This file investigates; it does not settle.*

## The evidence each candidate has

### 1. COBOL-era batch ledger systems (1960s–70s business computing)
- **For:** The era's business ledger literally was a master file —
  accounts as records, updated in overnight batch runs that squeezed
  scarce mainframe time. Casey's working life (IT consulting for
  small businesses) is full of these systems' descendants.
  **Phonetics is the strongest signal in this whole file:**
  "Cabos" ≈ *COBOL* misheard (/ˈkoʊ.bɒl/ → /kəˈboʊs/) is closer
  than any other candidate's name.
- **Against:** It's a class, not a named system; Casey usually names
  specific things.

### 2. Double-entry bookkeeping (Pacioli, 1494)
- **For:** It is *the* ledger — every transaction written twice,
  accounts arranged as a chart (a sheet of addressed cells), and it
  pairs naturally with PLATO's sheet: the grid of accounts is the
  oldest addressed data structure in business. Standard history:
  Luca Pacioli published the method in his *Summa* of 1494.
- **Against:** Not a computer system; Casey framed scarcity-era
  *computing*. No phonetic resemblance at all.

### 3. SABRE (IBM + American Airlines, online 1964)
- **For:** A single shared, real-time ledger of seat inventory —
  arguably the first online transaction processing system — with
  ~1,200 terminals reading and writing one book, 7,500 reservations
  an hour on two IBM 7090s. If "ledger" means "one authoritative
  record many terminals transact against," SABRE is the archetype,
  and its squeeze-every-cycle engineering ethos matches Casey's
  description exactly.
- **Against:** Casey knows SABRE's name and story; a garble of a
  famous two-syllable name into "Cabos" is less likely. "Ledger" is
  metaphorical for a reservation system.
- Sources: https://en.wikipedia.org/wiki/Sabre_(computer_system) ·
  https://www.computerworld.com/article/1705607/sidebar-sabre-timeline.html

### 4. Codd's relational model (CACM, June 1970)
- **For:** Relations are tables — rows in an addressed grid — and
  Codd's whole argument (data independence: state the logical shape
  once, never mind the physical layout) rhymes with "grid, not
  tape" and with the sheet. A ledger stored relationally is rows
  with addresses.
- **Against:** A data model, not a ledger system; nobody calls it
  ledger-based. Phonetics weakest of the four (one syllable).
- Sources: https://en.wikipedia.org/wiki/A_Relational_Model_of_Data_for_Large_Shared_Data_Banks ·
  https://amturing.acm.org/bib/codd_1000892.cfm

### Late candidate, NOT ranked: CODASYL
- The CODASYL Data Base Task Group (1971) standardized the
  navigational ("ledger-like" master/detail) databases Codd argued
  against. Phonetically middling, semantically plausible, surfaced
  after the Jev call — flagged for a follow-up, not silently added
  to the ranking. Dismissed outright: *Cabos*, the 2000s Gnutella
  file-sharing client — phonetically exact, but not a ledger and
  wrong everything else.

## Jev ranking (TypeSafe/Jev `choice`, 2026-10-12)

Question put to Jev: given Casey's framing (PLATO's sheet + an old
ledger-based system from the scarcity era), which candidate did he
most likely mean?

| Candidate | Jev probability |
|---|---|
| COBOL-era batch ledgers | **0.57** |
| Double-entry bookkeeping | 0.25 |
| SABRE | 0.18 |
| Codd's relational model | ~0.00 (not returned) |

Picked: **cobol_batch**, confidence **0.35** — a plurality, not a
verdict.

## Conclusion: OPEN

The honest state: the *shape* Casey wants is clear even with the
name unresolved — **PLATO's addressed sheet + a ledger discipline:
one authoritative record, transactions against addressed accounts,
engineered for scarcity.** Any of the top three candidates supplies
that discipline. The name itself stays an open question; the
cheapest resolution is one line to Casey ("COBOL? SABRE? the
double-entry books?"). Filed UNRESOLVED by design.

## Open questions

- Does the ranking change if "ledger" is weighted over "computer
  system" (pushes double-entry up) or over "named thing Casey would
  cite" (pushes SABRE up)?
- CODASYL: worth a second Jev round with five candidates?

*Status: investigation complete, identification UNVERIFIED.*

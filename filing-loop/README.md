# xero-filing-prototype

Chat-to-git filing loop — the prototype of the memory ladder's second rung
(the "better-than-that filing system" from the 2026-10-10 zero-agent ramble).

## What it does

Chat **tosses** utterances in; the loop **refines** them; everything
**checks in** to git. The git log is the ledger.

1. **Deposit** — an utterance (text + timestamp + source) appends to
   `inbox/<chat>/current.md` and commits.
2. **Cascade split** — split policy is gates: a *size gate* and a *time gate*.
   - L1: inbox file over the size gate → entries roll into daily archive
     files, `archive/<chat>/YYYY-MM-DD.md`.
   - L2: a single day still over the gate → that day splits by topic into
     `archive/<chat>/YYYY-MM-DD/<topic>.md`.
3. **Refine** (the idle-churn pass) — builds topic views over all source
   entries (`topics/<chat>/<topic>.md`) plus an `INDEX.md`. Views are
   regenerated wholesale, so refine is idempotent — run it any time.

Default size gate: 60,000 bytes (≈ the "~20 pages" from the ramble).
Demo uses 1,000 so the cascade visibly fires.

## Run it

```bash
python3 demo.py                 # end-to-end: 35 deposits, splits, refine, verify
python3 filing_loop.py init   store
python3 filing_loop.py deposit store <chat> "text" [--ts ISO] [--source NAME]
python3 filing_loop.py refine store [chat]
python3 filing_loop.py status store
```

Config via env: `FILING_SPLIT_BYTES`, `FILING_TOPIC_K`.
Pure stdlib Python 3. The demo store lands in `./store/` (a git repo).

Verified 2026-10-12: 35/35 entries survive deposit → L1 → L2 → refine;
second refine is a no-op (no commit, clean tree); deposits keep working
after refine.

## What's stubbed (honest list)

- **Topic assignment is a keyword-frequency heuristic.** This is the slot
  where an LLM iteration-box pass belongs — the design's topic-parse
  during idle churn. The heuristic is deterministic so the demo is
  reproducible; the interface (`top_keywords`, `primary_topic`) is the seam.
- **No live Telegram hook yet.** Deposit is a function/CLI — wiring it to
  the bridge (message arrives → deposit) is the next rung.
- **L2 simplification:** after a day splits into a topic directory, a later
  L1 append for the same day recreates the flat daily file alongside it.
  Readers handle both; production policy should append into the day-dir.
- Thresholds are bytes, not semantic "pages" — fine for a gate, worth
  revisiting when real chat flows through it.

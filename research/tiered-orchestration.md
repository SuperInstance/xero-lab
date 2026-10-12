# Tiered orchestration — cascades, decomposition, AutoResearch

*Xero Research Library · 2026-10-12*
*Framing: an addition layer. These are orchestration patterns Zero
may call on; the pyramid is a way of spending calls, not a part of
what Zero is.*

## The shape Casey is building toward

**1 : 20 : 100** — one small frontier-model call, engineered by
~20 medium-model coordination calls, fed by ~100 small-model calls.
The frontier call is kept *small* on purpose: the pyramid's work
goes into preparing its context and checking its output, so the
expensive judgment is spent once, on a well-posed question.

## Model cascades and routing (the published base)

- **FrugalGPT** (Chen, Zaharia & Zou, 2023) is the canonical
  cascade design: order models cheap→dear; after each generation, a
  **scorer** judges whether the answer is good enough to accept or
  whether to escalate to the next model. The paper reported matching
  frontier quality at a small fraction of the cost on its test
  workloads. *Specific percentages are UNVERIFIED in this pass (the
  source search failed); verify against the paper before quoting
  numbers.*
- **Confidence-based escalation** is the same idea without a learned
  scorer: small model answers, a cheap check (self-consistency,
  verifier, schema validation) decides accept-or-escalate.
- **Router classifiers** assign the tier *before* generation from
  features of the request (length, domain, difficulty estimate).
  Routers are cheaper than cascades when most traffic is easy;
  cascades are safer when difficulty is only visible in the answer.
- The pattern that matters for Xero: **the judge is a separate,
  cheaper thing than the judged.** Every tier transition needs an
  accept test, or the pyramid is just three prices of guessing.

## Decomposition (the middle of the pyramid)

The documented working pattern: a coordinator (medium tier) splits
a job into subtasks small enough for the bottom tier, fans them out
in parallel, then integrates and checks the results. The frontier
call is reserved for the one sub-problem that is actually hard —
or for designing the decomposition itself. Failure mode to design
against: integration cost. Twenty medium calls of glue can eat the
savings if subtask outputs need heavy reconciliation; keep subtask
contracts (schemas, file formats) fixed and boring.

## AutoResearch — the overnight loop, verified details

Andrej Karpathy's `autoresearch` (github.com/karpathy/autoresearch)
is the cleanest public reference for an agent improving a system
against a fixed scorer:

- **Three files, three roles.** `program.md` — human-written
  instructions, static; the human programs the *organization*, not
  the experiments. `train.py` — the **sole mutable file**.
  `prepare.py` — the fixed harness: data pipeline, tokenizer, and
  the `evaluate_bpb` scorer. The agent may never edit the scorer.
- **The loop.** Propose a change → run a **fixed 5-minute (300 s)**
  training budget → score **validation bits-per-byte (val_bpb)**,
  chosen because it is vocabulary-size-independent, so unlike
  architectures compare fairly → **commit if strictly improved,
  else `git reset --hard`** → log every attempt to `results.tsv` →
  repeat, ~12 experiments/hour, no pausing to ask the human.
- **Documented results** (write-ups vary by run): one overnight run
  logged 89 experiments, 15 kept / 74 discarded / 0 crashes, val_bpb
  0.997900 → 0.977287 on an H100; another account reports 126
  experiments in a night reaching 0.9697, and ~700 experiments over
  two days for ~11% improvement, including finding a long-missed
  bug in the human's own attention code.
- **Anti-gaming is structural**: scorer immutability + single-file
  scope. Known traps: the short-horizon metric itself can be gamed
  (a fork's "speedup" that only optimized the 5-minute proxy), and
  the strict ratchet forbids temporary regressions, so local minima
  are inescapable by design.
- Sources: https://github.com/karpathy/autoresearch ·
  https://github.com/maystudios/better-second-brain/blob/HEAD/wiki/sources/karpathy-autoresearch.md ·
  https://www.the-ai-corner.com/p/karpathy-autoresearch-method

Karpathy's name for the surrounding shift — developers spending
their time directing and reviewing agents rather than writing code —
is **"agentic engineering"**; the capability-gap framing around it:
https://thenewstack.io/karpathy-levie-ai-capability-gap/

## Patterns a builder can call on for a 1 : 20 : 100 pyramid

1. **Fix the scorer before the swarm.** The "1" call is only as
   good as the accept test under it. Write the rubric/eval first;
   freeze it; let everything below it be mutable.
2. **One mutable artifact per loop.** Scope is the safety system.
   (AutoResearch: one file. Xero: one cell of the grid.)
3. **Log every attempt, kept or not.** `results.tsv` is the active
   ledger of the pyramid: the discards are data — they map the local
   terrain the ratchet is climbing.
4. **Time-box every experiment identically.** Fair comparison beats
   best-effort runs; equal budgets are what make a score a score.
5. **The human writes `program.md`.** Instructions to the research
   organization — goals, constraints, success criteria — are the
   highest-leverage text in the system and the cheapest to change.
6. **Escalation needs a written accept test at every tier
   boundary** (FrugalGPT's scorer, generalized): 100→20 and 20→1
   each get a judge, and the judges are small, fixed, and boring.

## Open questions

- What is Xero's `val_bpb` — the single scalar a Xero ratchet would
  climb? (Candidates: filing accuracy, alarm precision, walkthrough
  reuse count. None chosen.)
- Ratchet vs. portfolio: AutoResearch keeps one lineage; Casey's
  fleet habits suggest parallel lineages with a judge (closer to the
  season/matrix pattern). Which fits a 1:20:100 budget?

*Status: AutoResearch details verified from public write-ups;
FrugalGPT figures UNVERIFIED pending a read of the paper.
Synthesis assisted by a MiniMax draft, 2026-10-12.*

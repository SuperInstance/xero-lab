# Zero-Shot Cold Playtest — SuperInstance/xero-lab

*2026-10-13 · Testers: fresh model instances (MiniMax-Text-01, GLM via ZAI)
given only material fetched from the public repo, plus one hands-on runner
following the READMEs literally inside a fresh `git clone`. No project lore,
no hints, no leading questions were given to any reader. Nothing in this
report was fixed — it is a record of friction, verbatim where possible.*

Routes used: MiniMax (`skills/minimax/bin/chat.py`, MiniMax-Text-01) and
ZAI (`skills/zai/bin/chat.py`, glm-4.5-flash) — two model families.
Cold-read calls: 4 total (2 per task), run sequentially, ≥3 s gaps,
zero HTTP 429s, zero errors. Hands-on work ran in
`~/workspace/xero-lab-playtest/clone/` (a clean clone of the public repo).

**A note on the hands-on environment:** the playtest machine is the
project's own VM, so absolute paths pointing into the author's workspace
*resolve* here. Where that contamination matters, the run was repeated
inside a mount namespace with the author's workspace directories hidden
("newcomer simulation") — that is the result a real newcomer gets.

---

## (a) Per-reader verdicts

### Task 1 — Cold read: landing page

**Reader 1A (MiniMax-Text-01).** Understood the project? **Yes** — "a blank
slate—an entity with limitless potential that becomes an agent through a
series of deliberate additions." Found something usable? **Yes** — walking
dictation, the bilge/deadband monitor pattern, the decision grid. First pick:
**the walking dictation** — "The ability to transcribe and organize thoughts
and conversations into markdown chunks is a powerful tool for productivity.
I would use it to capture ideas and notes during meetings or brainstorming
sessions."

**Reader 1B (GLM/ZAI).** Understood the project? **Yes** — "Instead of
starting with a pre-built 'harness' (like a large language model) and adding
features, it begins as a blank slate—pure potential with zero innate
capabilities." Found something usable? **Yes** — voice cadence, decision
grid, filing loop. First pick: **the voice transcription** — "It's a real
prototype (not simulated), with quantified metrics (e.g., 'Patient held 499
words' vs. 'Eager answered 45 times')… I'd reuse the 'cadence' logic (emit
at 60s/page/gap) and integrate it with existing ASR APIs."

**Both landing readers picked the voice block first, unprompted and
independently.**

### Task 2 — Cold read: repo front door (README.md + research/INDEX.md + tree)

**Reader 2A (MiniMax-Text-01).** Start: README → research/INDEX. Found the
reusable thing? **Yes — filing-loop**, via the README's "✅ working" mark and
its DEMO-OUTPUT receipts. Missing for a newcomer: setup/install instructions,
examples/tutorials, testing instructions, CONTRIBUTING, and a license —
"The repository does not include a license file. A license is essential for
clarifying how others can use, modify, and distribute the code."

**Reader 2B (GLM/ZAI).** Start: README → research/INDEX → nuggets.md. Found
the reusable thing? **Yes — filing-loop**: "it could be valuable for any
project needing to manage conversational data with git integration." Missing:
setup instructions, API documentation, dependency information, and a clear
experimental-vs-stable distinction. Its summary of the whole repo's problem:
the README says "An agent is a set of files; the harness is just the crank
that turns them," but "it doesn't explain how to build that crank or turn it."

**Neither front-door reader could identify what `landing.html` or
`deployment.html` are** — the tree shows them, nothing in README.md or
INDEX.md mentions them, and the root README's "What's here" section covers
only `filing-loop/` and `notes/`. The majority of the repo (voice-block/,
wave-language/, decision-grid/, research/, both HTML pages) is invisible
from the front door.

### Task 3 — Hands-on: filing loop

**Verdict: flawless.** `python3 demo.py` ran first try: 35 deposits, splits,
refine, "verify: 35 source entries on disk, 35 deposited -> OK", "git: 42
commits (the ledger)". The full documented CLI (`init`, `deposit` with
`--ts`/`--source`, `refine`, `status`) worked verbatim on both the demo
store and a fresh store. The README is sufficient, complete, and honest
(including its "What's stubbed" list).

### Task 4 — Hands-on: voice block

**Verdict: the Python half works once you guess the right directory; the
headline worker command in the main README is broken verbatim.** Segmenter:
16/16 tests pass, demo reproduces the published numbers. Modes simulator
runs from the voice-block root with no instructions needed beyond its
existence. Worker: the main README's `node --test test/` fails on Node 24;
the working route (`npm test`, 8/8, no install) is documented only in
worker/README.md.

### Task 5 — Hands-on (lighter): wave language + decision grid

**Wave language: the offline three-quarters runs beautifully; the headline
test cannot start cold.** `sea.py`, `make_samples.py`, and `daylog.py` all
run first try, and daylog's table matches RESULTS.md byte-for-byte
(46,386,706 B raw numeric, etc.). `reading_test.py` — the actual claim
test — dies at import on any machine but the author's.

**Decision grid: no documented command runs from the clone at all.** Every
script in `code/` hard-codes absolute paths into the author's own workspace
(`/home/hatch/workspace/...`). On the author's machine the commands appear
to work — while silently reading and writing a *different directory* than
the clone. On a newcomer's machine the first documented command fails
instantly. This is the most damaging finding of the playtest (see stumble
DG-1).

---

## (b) The stumble log

### Cold-read stumbles (readers' own words)

**CR-1 — Real-vs-simulated labels don't form a system (landing page).**
The eight cards carry five different status vocabularies: "Real prototype",
"Simulation", "Measured — staircases closed", "Measured — v3: settled",
"Simulation · measured in the fleet". Reader 1B: "Demo Labeling: Unclear
which demos are real vs. simulated. The 'walking dictation' is labeled
'real prototype,' while others like '3 a.m. bilge' are 'simulation,' but
the page mixes them without clear separation." The same reader misread the
bilge card as "Labeled 'simulation' but described as 'real prototype'
elsewhere" and the combadge as "Described as 'real prototype' but lacks
implementation details" — the labels are individually honest but a cold
reader cannot assemble them into a stable model of what exists.

**CR-2 — The combadge's core rule is asserted, never explained (landing).**
Reader 1A: "It's unclear how the system determines which brain can 'hold'
the question and how it handles the transition between different brains."

**CR-3 — The 5,231-repo claim has no visible methodology (landing).**
Reader 1B: "Claims analysis of 5,231 repos, but no methodology or
examples." (The methodology exists — research/superinstance/SURVEY.md —
but the landing page does not link to it, and neither front-door reader
was led to it.)

**CR-4 — The philosophy layer reads as abstraction without a handle
(landing).** Reader 1B on zero-innate: "'The agent is the story. The loop
is the machine.' lacks actionable guidance." Reader 1A on the record-
folding card: "it's unclear how this works in practice and what the
implications are for real-time systems." Reader 1B on the ternary
rejection: "Claims 'balanced ternary... failed it' (score 0.06) but
doesn't explain why"; on the UNO Q: "called the 'bottom rung' with no
proof."

**CR-5 — Front door assumes insider vocabulary (README + INDEX).**
Reader 2A: "The README.md is informative but assumes a certain level of
familiarity with the 'Xero' project and its terminology (e.g., 'redshirt
split,' 'desert-island learning loop')." Public docs also name a person —
"Casey's 2026-10-12 ramble" (research/INDEX.md), "Casey's 2026-10-12
seed" (wave-language and decision-grid READMEs) — with no indication of
who that is or why his rambles are load-bearing.

**CR-6 — No way to run anything from the front door (README).** Both
front-door readers, independently: no setup instructions, no quickstart,
no dependency information, no test instructions. Reader 2A: "the
`filing-loop/` folder contains a `demo.py` file, but there are no
instructions on how to execute it" (from the front door's materials —
filing-loop's own README does document it, one level down).

**CR-7 — No license (repo-wide).** Reader 2A: "The repository does not
include a license file." Reader 2B lists the same gap. For a repo whose
landing page invites reuse, this blocks the exact visitors it attracts.

### Hands-on stumbles (verbatim)

**FL-1 — Filing loop: silent success (soft).** `init`, `deposit`, and
`refine` print nothing at all on success (exit 0, no output). The only
confirmation a newcomer ever gets is running `status`. Everything worked
— but three of the four documented commands give zero feedback that they
did anything.

**VB-1 — Voice block: unstated working directory (segmenter tests).**
README's layout block gives `python3 -m unittest test_segmenter` beside
the file listing but never says to `cd segmenter` first. From
`voice-block/`:

```
$ python3 -m unittest test_segmenter
ModuleNotFoundError: No module named 'test_segmenter'
FAILED (errors=1)   EXIT=1
```

From `voice-block/segmenter/`: `Ran 16 tests in 0.068s — OK`.

**VB-2 — Voice block: the headline worker command is broken (main
README).** voice-block/README.md's layout says: `node --test test/  → 8
tests`. Verbatim, on Node v24.20.0:

```
$ node --test test/
Error: Cannot find module '/home/hatch/workspace/xero-lab-playtest/clone/voice-block/worker/test'
✖ tests 1 · pass 0 · fail 1   EXIT=1
```

The working command is `npm test` (package.json's script names the two
test files explicitly) — documented only in worker/README.md. Via
`npm test`: "tests 8 · pass 8 · fail 0", no `npm install` needed.

**WL-1 — Wave language: the reading test cannot start on a newcomer's
machine.** wave-language/README.md's "Run it" lists
`python3 reading_test.py --streams 36   # the reading test (MiniMax)` —
with no explanation anywhere of what provides MiniMax access or what
credentials are needed. reading_test.py:22 hard-codes
`sys.path.insert(0, "/home/hatch/workspace/skills/minimax/bin")`.
Newcomer simulation (author paths hidden):

```
$ python3 reading_test.py --streams 1
ModuleNotFoundError: No module named 'chat'   EXIT=1
```

**DG-1 — Decision grid: every script hard-codes the author's absolute
paths (the playtest's most damaging stumble).** All 11 files in
`decision-grid/code/` reference `/home/hatch/workspace/...`:

- `sample.py:9` — `SRC = "/home/hatch/workspace/xero-research/superinstance/.scratch/all-repos.jsonl"` (a file that is not in this repo at all); `:10` — output goes to `/home/hatch/workspace/xero-decision-grid/data/sample.jsonl`.
- `algo.py:12-13`, `score.py:11`, `score2.py:16`, `finalize.py:10`,
  `finalize2.py:21`, `big_sample.py:4`, `jev_gates.py:9`,
  `jev_rerun.py:10`, `minimax_run.py:11`, `minimax_paced.py:24` — all
  data paths point at the author's dev folder `xero-decision-grid/`,
  never at the repo the code ships in.
- `finalize.py:24`, `finalize2.py:35`, `minimax_run.py:16`,
  `minimax_paced.py:41` — also read the external enumeration directly.
- `jev_gates.py:8` / `jev_rerun.py:9` — `JEV = "/home/hatch/workspace/skills/typesafe/bin/jev.py"`; `minimax_run.py:10` / `minimax_paced.py:23` — the author's MiniMax skill CLI, same pattern.

Consequences, both verified by running:
1. *On the author's machine* the documented sequence appears to succeed
   and reproduces the published numbers (1,580 sheet rows, "staffed
   grid: 3391.3 units (8.6% of all-BIG)") — but it reads and writes the
   author's dev directory the whole time. The clone's own committed
   `data/` is never touched. The author cannot discover this breakage
   from his own machine.
2. *On any other machine* (newcomer simulation, author paths hidden),
   the README's very first command dies:
   `FileNotFoundError: [Errno 2] No such file or directory: '/home/hatch/workspace/xero-research/superinstance/.scratch/all-repos.jsonl'` (sample.py, EXIT=1), and the second dies the same way on
   `'/home/hatch/workspace/xero-decision-grid/data/sample.jsonl'`
   (algo.py, EXIT=1). **Zero of the decision grid's documented commands
   run from the public repo alone** — despite RESULTS.md's numbers being
   real and reproducible (they reproduced here, against the dev copy).

**DG-2 — Decision grid README's data-source line names a path newcomers
can't have.** "Data source: `~/workspace/xero-research/superinstance/.scratch/all-repos.jsonl` (the survey's full 5,231-repo enumeration)" — stated
plainly, but with no vendored copy, no generation instructions a newcomer
can complete, and no note that the committed `data/sample.jsonl` makes
most of the pipeline re-runnable without it.

**DOC-1 — Stale index (research/INDEX.md).** The survey row reads
"Separate coordinator's file — in progress elsewhere" — but
`research/superinstance/SURVEY.md` is complete and ships in the same
repo. The Provenance section says "Nothing here is pushed to GitHub by
this library's builders" — in a file served from GitHub.

**DOC-2 — Process notes leaked into public docs as false status claims.**
voice-block/README.md ends "*Nothing here is pushed to GitHub. Parent
reviews first.*"; wave-language/README.md ends "No GitHub push; built as
a seed"; decision-grid/README.md says "No GitHub push; no secrets
anywhere in the tree". All three sit in the public repo they claim not
to be in. A newcomer cannot tell whether these are status, superstition,
or irony.

---

## (c) Ranked fix list

1. **`decision-grid/code/*.py` (all 11 files)** — Replace every
   `/home/hatch/workspace/...` absolute path with paths resolved
   relative to the script/repo (`Path(__file__).resolve().parents[1]`),
   and make the pipeline run from the committed `data/sample.jsonl`
   by default; treat the 5,231-repo enumeration as an optional
   regeneration input, vendored or fetched, not a requirement.
   *Proven by DG-1: the first two documented commands fail cold with
   FileNotFoundError, and on the author's machine the code silently
   operates outside the clone.*
2. **`README.md` (root)** — Rewrite "What's here" to cover every
   top-level folder (voice-block/, wave-language/, decision-grid/,
   research/) and state what `landing.html` and `deployment.html` are,
   with links. *Proven by Task 2: both readers found only filing-loop +
   notes from the front door; neither could identify the HTML pages.*
3. **Repo root** — Add a `LICENSE` file, and add a five-line
   "Run something in two minutes" quickstart to README.md pointing at
   `filing-loop`'s demo and the voice-block tests. *Proven by CR-6 +
   CR-7: both front-door readers independently listed license and
   setup instructions as the missing basics.*
4. **`voice-block/README.md`** — Change the worker line to `npm test`
   (matching worker/README.md and package.json) and state the working
   directory for every command in the layout block (`cd segmenter`
   before the unittest line). *Proven by VB-1 and VB-2, verbatim.*
5. **`landing.html`** — Collapse the five status vocabularies into two
   or three terms defined once in a legend above the gallery (e.g.
   REAL PROTOTYPE / MEASURED RUN / SIMULATION), and apply them
   uniformly. *Proven by CR-1: Reader 1B could not tell what's real vs
   simulated and misread two cards' status.*
6. **`wave-language/reading_test.py` + `wave-language/README.md`** —
   Document the MiniMax dependency where the command is listed (what
   the `chat` module is, how a runner supplies it or a key), or read
   the endpoint/key from environment variables via stdlib. *Proven by
   WL-1: `ModuleNotFoundError: No module named 'chat'` is the
   newcomer's first and only result.*
7. **`research/INDEX.md`** — Refresh the survey row (complete, in this
   repo) and remove or rewrite the "not pushed to GitHub" provenance
   line. *Proven by DOC-1: the index contradicts the repo it ships in.*
8. **`voice-block/README.md`, `wave-language/README.md`,
   `decision-grid/README.md`** — Delete the "No GitHub push / Nothing
   here is pushed to GitHub / Parent reviews first" lines (internal
   process notes). *Proven by DOC-2: all three are false on their face
   in the public repo and read as status claims.*
9. **`landing.html`** — Link the 5,231-repo figure to
   `research/superinstance/SURVEY.md`, and give the combadge card one
   sentence on how the smallest-brain rule decides. *Proven by CR-3
   (skepticism with no methodology visible) and CR-2 ("how the system
   determines which brain can 'hold' the question").*

---

## (d) What delighted the cold readers (keep these — they're load-bearing)

- **The voice block's Patient mode is the single most delightful find.**
  Both landing readers picked it first, independently, and immediately
  designed a use for it. Reader 1B: "The 'Patient' mode for voice input
  (ignores silences >5s, emits at 60s/page gaps) solves a real pain
  point in voice agents." Reader 1A: the toggle between cadences "would
  allow me to customize the transcription behavior based on the
  context."
- **The filing loop runs exactly as documented — the trust anchor of
  the repo.** Both front-door readers chose it as the thing they'd
  reuse (the "✅ working" + receipts pattern worked: Reader 2B found it
  "by looking at the README's component descriptions and identifying
  the one explicitly marked as working with verification results"), and
  hands-on it delivered: 35/35, idempotent, zero surprises. Its
  "What's stubbed (honest list)" section is the tone the whole repo
  benefits from.
- **The confidence column in research/INDEX.md.** Reader 2A called the
  "topic → file → gist → confidence" structure "incredibly useful for
  quickly identifying relevant materials and understanding their status
  (verified, unverified, etc.)". Honest UNVERIFIED marks made the
  verified claims *more* credible, not less.
- **Measured numbers with receipts.** Reader 1B trusted the voice
  prototype precisely because it was "a real prototype (not simulated),
  with quantified metrics ('Patient held 499 words' vs. 'Eager
  answered 45 times')". Hands-on, the published numbers reproduced:
  daylog's table byte-for-byte, the grid's 8.6%-of-all-BIG staffing,
  the segmenter's 0% mid-sentence chunk endings vs the naive baseline's
  82–100%.
- **The deadband/bilge pattern as a transferable idea.** Reader 1A
  lifted it out of the maritime frame unprompted: "This could be
  adapted for monitoring other types of thresholds in systems where
  constant monitoring and minimal alerts are desired."
- **The decision-grid concept** ("Put the work in cells. The big
  model's job is the cut") landed with both landing readers as usable
  today — which is exactly why its unrunnable code (DG-1) is the
  playtest's most damaging stumble: the idea sells, the repo can't
  cash the check.

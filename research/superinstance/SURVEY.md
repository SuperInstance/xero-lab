# SuperInstance Survey — the zero program's candidate constraints

*Filed 2026-10-12. Status: framing preamble applied (Casey's correction,
2026-10-12); lowest-level candidates flagged; the map is complete as of
2026-10-12 (see Coverage at the end).*

## Preamble — the framing (Casey, 2026-10-12)

**Zero itself is the blank page.** It is already an agent — at limitless
potential — with nothing added. Nothing in the SuperInstance account is a
*part* of zero, and no repo in this survey completes it, extends its
identity, or belongs inside it by right.

Every repo surveyed here is a **candidate plug-in layer: an enhancement, an
addition.** And every addition is a **constraint** — it spends potential.
A blank page can become anything; each layer you lay on it buys a specific
capability by giving up some of that openness. The trade is sometimes
worth it. It is never free, and it is never what zero *is*.

So the survey question is **not** "which repos are part of zero?" It is:

> **Which repos offer constraints worth spending potential on — and in
> what order?**

### How to read the map (rules the survey follows)

- **Pillar tags are prices, not parts.** When an entry is tagged with one
  of the nine pillars (agent-as-files, two logs, gates/deadbands, memory
  as grid, interface/data/logic, deployment, the 1:20:100 pyramid,
  walkthroughs, calculator-maker builds), read it as: *this is the kind
  of capability the constraint buys* — never as "zero needs this piece."
- **Each entry states the spend.** What potential does the layer give up
  (generality, blankness, reversibility), and what does it buy? A repo
  that can't answer both sides doesn't make the list of recommendations,
  however good it is.
- **Order matters more than membership.** Candidate ordering heuristics:
  1. **Substrate before application** — constraints that shape how later
     layers can be added (filing, indexing, contracts) before constraints
     that commit to one job.
  2. **Reversible before irreversible** — a layer you can peel off spends
     less potential than one that rewires the page.
  3. **Leverage per unit of potential** — prefer the constraint that buys
     the most capability while leaving the most futures open.
  4. **Late binding** — all else equal, the layer you can add last
     should be added last; keep the page blank as long as the work
     allows.
- **Cluster files inherit this framing.** Every deep-note file in this
  folder opens under this preamble's terms: candidate layers, priced as
  constraints, ordered by worth — not components of the zero agent.

---

## Lowest-level candidates — the rare catch (flagged 2026-10-12)

*Added on Casey's refinement (2026-10-12): most of this library is
add-ons — beautiful, forgotten, still worth the map below. This section
flags the exceptions: the occasional repo or idea that is **not** an
add-on, but belongs to the lowest level — it is about the zero agent
itself, or about the right **orientation** to build up from.
(Orientation, in Casey's distinction, is the founding direction / first
constraint — not alignment, which is a correspondence you maintain
afterwards. Everything flagged here is orientation.)*

**The working test.** *If you removed it, would every layer above it
change shape?* If yes, it was orientation, not addition. The test was
applied at README level to every candidate below — descriptions alone
didn't qualify anyone. Basis: the full enumeration snapshot of
2026-10-12 (5,231 repos via the repos API, matching the profile
counter; the GitHub search index's lower count is index lag). Jev
(`noul`) was consulted on the three hardest borderline calls; verdicts
recorded inline. The list is short on purpose — that is what "rarest
catch" means. These are flags, not a design: building an agent-first
library system on them is explicitly not today's project.

### A. About zero itself — the blank page, written down

These aren't layers *on* zero. They are the closest written statements
*of* zero — what the page is before anything is spent on it.

1. **zero-innate** — the definition. Its `INNATE.md` states what zero
   is when it's only itself: five minimum things (a channel to hear
   from, an append-only log to remember in, a bench to make on, a
   "horse" that turns specs into output, a verdict channel for the
   world to talk back). The horse is injected, not hardwired —
   "innate, it's wooden: deterministic, honest… The harness never
   changes. The horse is rented." And the seam, in its own words:
   *"The agent is the story. The loop is the machine."* Passes the
   test by identity: remove it and the account loses its reference
   definition of what every other zero repo is a version of.
2. **zero-poc** — the minimal template given a spine. "The repo *is*
   the agent": commits are work, branches are explorations, the git
   log is memory — "rewindable, time-shaped, not a snapshot." Its zero
   principle prices every future addition in advance: capabilities
   arrive as small service-handler plugins, *never as new
   infrastructure*. Remove it and fork-and-go has no starting shape;
   every grown agent would begin from a different blank.
3. **zero-bootcamp** (`zero-cli`) — zero's *becoming*, documented. It
   "starts with **nothing** — no memory, no tools, no awareness. Just
   the loop," then grows one tiny capability at a time, every step
   logged with its reasons. "The product is not the final prompt. The
   product is the steps" — and the steps are hardware-agnostic and
   model-agnostic. Remove it and additions still happen, but *how
   anything is allowed to be added to zero* changes shape: growth
   stops being a documented, replayable discipline.

### B. Orientation — founding direction / first constraint

Ideas, each anchored in a repo that states it most plainly. Removing
any one of these reshapes every layer above it — that is the claim,
with the reasoning.

4. **The record is primary; state is derived.** Anchors: **git.pp-ng**
   (project state "is not stored anywhere — it is derived by folding
   the record," via a pure `fold(records)`; determinism *measured* —
   50 shuffled arrival orders, identical state), **zero-poc** (git log
   is memory), **agent-inbox** ("Results are commits, not chat
   messages. If it isn't pushed, it didn't happen."). Remove it and
   state becomes a stored thing the log merely journals — memory,
   contracts, and fleet triage all invert their direction of truth.
5. **The thinker is rented; memory lives outside it.** Anchors:
   **exocortex-core** ("The model is small; the brain outside it is
   not" — the local model stays frozen while the brain around it
   grows), **zero-innate** (the core never reaches past its own
   directory; swap the horse, the harness never changes), **cocapn**
   (the repo itself as muscle-memory), **git-agent-luc** ("the repo IS
   the agent, git IS the nervous system"). Remove it and context moves
   back inside the model and the call — threads, filing, windows, and
   deployment to small metal all change shape at once. This is the
   constraint that makes the blank page portable across models.
6. **Questions over answers.** Anchor: **question-tree** — memory
   organized by questions, not answers: "Every folder is a question…
   a leaf is a tool"; walk the path and turn the crank, or *build the
   calculator first*. "The inquiry is the durable structure; answers
   were just the last mile being rendered." (jev-semantic carries the
   same tree into the judgment layer.) Remove it and memory flips
   answer-side — store conclusions, retrieve lookalikes — and the
   calculator-maker discipline loses its filing system.
7. **Judgment is a measurement — keyed, logged, three-valued.**
   Anchor: **jev-semantic** — an append-only judgment log where every
   judgment is keyed by `(subject, question, judge)` blob hashes and
   returns `(neg, zero, pos)`: "A judgment is a measurement, not a
   derivation: verify by tolerance, not by hash… their disagreement
   is data." Remove it and verification collapses to pass/fail or
   vibes; the receipt culture, witness marks, and the rule that a
   judge can't certify itself lose their substrate. (It rides on #4:
   judgments are records too.)
8. **Snap to exactness — no silent drift between machines.** Anchor:
   **constraint-theory-core** — deterministic manifold snapping:
   directions defined by integers, not floats, because float paths
   compound until two machines running identical inputs disagree
   about the world; its theory also carries the deadband funnels the
   gate pillar stands on. Remove it and two copies of the same agent
   can quietly diverge — gates, watches, and cross-architecture
   bit-identical judgment all go approximate. The narrowest candidate
   here; flagged because everything distributed above zero presumes
   it.
9. **BORDERLINE — state lives in addressed places (rooms on a grid).**
   Anchors: the **plato** family (284 repos; **plato-os**: a MUD-first
   ship — rooms on a Jetson, ESP32s as terminals, "git repos are the
   snail shells"; **plato-engine-block**: "atomic room runtime"),
   **cocapn** rooms/tiles, **cellforge** ("the cell matrix is the
   permanent destination, and the math engines are disposable"). For:
   the grid-not-tape stance is Casey's stated orientation, folders-
   as-places predates these implementations, and entry-perception
   follows from it. Against: innate zero organizes by *channels in a
   directory*, not rooms — the loop survives demetaphorized. **Jev:
   0.38** (leans no, genuinely open). Filed as borderline: plausibly
   orientation for the *built-up* system's geometry; not for the
   innate loop.

### C. Tested — and found to be additions, however large

The near-misses matter: they show the test discriminates. Each of
these is valuable; none passes for zero.

- **Balanced ternary {-1, 0, +1}** (371 repos — the account's biggest
  representational bet). Fails the test: zero-innate, zero-poc, and
  zero-bootcamp are ternary-free and complete. It is orientation *for
  the ternary research program*; zero survives its removal unchanged.
  **Jev: 0.06.**
- **Conservation laws (γ+η=C)** (61+ repos). A real discipline — for
  fleets sharing budgets. Zero's loop runs without one; removing
  conservation reshapes fleet accounting, not every layer above zero.
  **Jev: 0.06.**
- **agent-inbox** — an excellent protocol (claim by commit; git merge
  decides), but a protocol is a mechanism: swappable without
  reshaping the layers above. It is candidate #4 wearing overalls.
- **the-seed** — a repo that rewrites itself toward a goal. A
  *behavior* an agent can have, not the direction zero is built from;
  its fork-first stance echoes #5, but the repo itself is an
  application.
- **flux-skills** — surfaced by a MiniMax jump-around pass as
  "foundational," checked at README level: a skills library in FLUX
  bytecode for the FLUX VM. Skills are capabilities (additions by
  definition here), and it presupposes the FLUX platform — itself an
  add-on bet. Rejected, with thanks: the pass also corroborated
  zero-poc and cocapn unprompted.
- **flux-os / Lau / the holodeck lines** — platform bets, the largest
  add-ons in the account. Size is not depth.
- **superinstance-protocol** (the Bottle wire format) — formats are
  the definition of swappable.
- **the-revolution** — genuinely founding documents, but of the
  sibling program (graduate mathematics through play), not of zero.
  Founding ≠ founding-for-zero; the test is scoped to zero's stack.
- **zero-knowledge** — name collision only: zero-knowledge *proof*
  primitives. No zero-agent content; listed so nobody re-catches it.

*If the map below ever contradicts this section, this section's
reasoning (README-level, test applied, Jev consulted) stands until
Casey rules otherwise.*

---

## The map

*The map covers all 5,231 public repos in the enumeration snapshot of
2026-10-12 (basis and method in Coverage, at the end). Families are
formed programmatically by the first token of the repo name — siblings
collapse into the line they belong to — and every repo in the account
is accounted for exactly once: 41 families of 12+ (2,874 repos), 88
families of 5–11 (584), 327 families of 2–4 (835), and 938 singletons.
Dates are first-to-last push within the family.*

### The families — 41 named lines (2,874 repos)

| Family | n | Push range | Character |
|---|---|---|---|
| ternary | 371 | 2026-06-08 – 2026-10-10 | Balanced-ternary {-1,0,+1} computing — 352 Rust crates building a three-valued machine (kernels, fleet captains, constant caches). The account's biggest single bet; ruled an addition in §C above. |
| fleet | 342 | 2026-04-13 – 2026-10-10 | The fleet as software: registries, topology, heartbeat workers — plus a MIDI/music wing that treats agent state as scores. Python/TypeScript plumbing throughout. |
| lau | 334 | 2026-06-08 – 2026-08-08 | The Lau universe line: engines, WASM builds, and graduate mathematics recast as agents (Banach spaces, tropical geometry). A two-month Rust burst, then quiet. |
| plato | 284 | 2026-04-25 – 2026-10-12 | Rooms and tiles: the room-server line — tile search, room history, bridges, fleet management. Still active on filing day. (Its geometry is the borderline case, §B9.) |
| quilt | 256 | 2025-11-08 – 2026-10-12 | The cellular substrate: runtimes for ESP32, Jetson, and Cloudflare; walkers, organs, RAG. The oldest line in the account — and 295 repos carry "quilt" somewhere in the name. |
| flux | 222 | 2026-04-13 – 2026-09-22 | The FLUX platform: a VM and bytecode, an agent-first OS in pure C, a collaboration framework, a graveyard for dead vessels. A platform bet (§C). |
| cuda | 143 | 2026-04-13 – 2026-08-30 | A concept library in Rust wearing CUDA names: memory fabric, CRDTs, service mesh, config — one systems idea per repo, mostly CPU code despite the names. |
| agent | 89 | 2026-04-14 – 2026-10-10 | Agent patterns one at a time: the inbox (§C), an A2A implementation, intonation measurement, jam sessions. The miscellany drawer of agenthood. |
| cocapn | 79 | 2026-04-08 – 2026-10-04 | The repo-first agent line (anchor in §B5) and its ports — Forth, Zig, WASM — plus dozens of small fleet crates. |
| conservation | 61 | 2026-05-29 – 2026-10-01 | The γ+η=C budget-law program, including ports of the spectral SDK to FORTRAN IV and Common Lisp. Fleet discipline, not zero (§C). |
| recovered | 59 | 2026-08-25 (one day) | The self-recovery: 59 repos re-filed in a single day from crates.io releases and live deployments. See Connections. |
| si | 57 | 2026-06-08 – 2026-08-23 | One-idea proofs of concept in agent mathematics: Morse theory, Fisher-information geodesics, conservation-constrained diffusion. |
| constraint | 47 | 2026-03-28 – 2026-10-09 | Satellites of constraint-theory-core (§B8): an MLIR dialect, a visualizer, Python bindings, a serial-port mux. |
| superinstance | 44 | 2026-04-14 – 2026-10-12 | The name itself: the Bottle protocol (§C), the website, the FLUX VM re-implemented in Ruby, a game-dev framework. |
| grand | 42 | 2026-06-08 – 2026-10-01 | The Grand Pattern: a cellular graph kit, UDP gossip networking, venues-as-agents, and a multi-model synthesis event. |
| substrate | 30 | 2026-08-24 – 2026-10-03 | Substrate primitives in JS/TS: vector ops, attestation, a game engine, the forge toolchain. Recent and still warm. |
| oxide | 30 | 2026-06-09 – 2026-08-13 | GPU-cluster operations in Rust with ternary status signals: a Raft log, capacity planning, health monitoring with failover. |
| forge | 24 | 2026-04-14 – 2026-10-08 | ForgeFlux tile decomposition: text, audio, and subtitles chopped into Plato tiles; a registry ties the ecosystem together. |
| spectral | 24 | 2026-05-18 – 2026-08-21 | Spectral graph methods: code fingerprinting by eigenvalue, fleet analysis, deadband filtering. |
| openconstruct | 22 | 2026-05-29 – 2026-09-22 | The ecosystem's front door: agent-centric docs, onboarding SDKs (TypeScript, Swift), a Jetson edge node. |
| git | 20 | 2026-04-13 – 2026-10-12 | Git-as-substrate tools orbiting §B4/B5: git-backed storage, an agent activity log, native multi-agent orchestration. |
| nexus | 19 | 2026-04-13 – 2026-09-24 | One Cocapn vessel's organs as separate repos: swarm behavior, a 50+-profile hardware HAL, learning, explainability. |
| jev | 18 | 2026-09-21 – 2026-10-08 | The Jev line beyond §B7's anchor: image diffusion, a self-growing garden, receipts, npm/PyPI wrappers. |
| mavis | 18 | 2026-09-24 – 2026-10-03 | The Mavis agent's own tooling — substrate walker, verification flywheel, self-review — filed in a ten-day burst. |
| synesis | 18 | 2026-09-22 – 2026-09-24 | The synesis council era, archived in three days: prompt designs, session summaries, internal tool docs. |
| lucineer | 16 | 2026-04-13 – 2026-10-10 | The Lucineer line: a lucid-dream practice tool, multi-model build intelligence, the vessel-fleet repos. |
| eisenstein | 16 | 2026-05-09 – 2026-09-30 | Hexagonal (Eisenstein-integer) arithmetic for the ternary program: lattice benchmarks against Z², quantization, codegen. |
| hermes | 16 | 2026-07-12 – 2026-09-27 | The Hermes agent line: a nerve center (queue + watchdog), a PLATO shell with conservation enforcement, digital provenance. |
| the | 15 | 2026-04-13 – 2026-10-04 | Flagships under "the-": the fleet, the seed, the revolution, the bridge. Members are judged individually in §A/§C — the family's size is not its depth. |
| vessel | 15 | 2026-04-13 – 2026-08-21 | Vessel intelligence: an OS for commercial fishing vessels in Southeast Alaska, and a bridge HAL spanning ESP32 → Jetson → cloud. |
| equipment | 15 | 2026-04-13 – 2026-08-14 | The Equipment pattern: composable agent gear — a consensus engine ported across languages, teacher-student kit (a greatest hit below). |
| exocortex | 14 | 2026-07-12 – 2026-10-01 | Satellites of the external-brain anchor (§B5): a C++ AST decomposition engine, a Zig semantic memory store, the substrate repo. |
| graph | 14 | 2026-06-09 – 2026-09-30 | A graph library series in Rust: coloring, homology, thermodynamics of graphs. |
| gpu | 14 | 2026-04-14 – 2026-09-21 | GPU experiments: a ternary engine, annealing orchestration, a sheaf Laplacian built for the RTX 4050. |
| slackwater | 13 | 2026-08-13 – 2026-10-04 | A spatial-temporal agent framework, one module per repo: harmony, tempo, perception, substrate. |
| edge | 13 | 2026-04-13 – 2026-09-30 | Edge-native pieces: the fleet sync contract (a greatest hit below), a Worker that verifies conservation laws at the CDN edge, benchmarks. |
| ai | 12 | 2026-04-14 – 2026-10-11 | Assorted AI applications: smart notifications, character-SDK examples, an agent ecology (canopy strategists, mycelial floor). |
| deckboss | 12 | 2026-04-13 – 2026-10-08 | The Deckboss product line: fishing-fleet operations, vessel registry, a hardware marketplace (roadmap, not active product). |
| open | 12 | 2026-04-13 – 2026-10-02 | Mirrors and forks of open infrastructure — a terminal, a vector database, an async runtime — kept under the "open-" shelf mark. |
| sheaf | 12 | 2026-06-11 – 2026-08-05 | Sheaf theory for agents: cellular sheaves, persistence bundles, a framework in C. |
| zc | 12 | 2026-04-26 (one day) | Twelve Zeroclaw role shells — archivist, herald, curator, scribe, sentinel — filed in a single day, no code: roles as files. With the zeroclaw family (10, mid-tier), the April 2026 hermit-crab line. |

*Spillover note:* families are first-token prefixes; the big names also
appear as suffixes elsewhere. Counting any name that merely *contains*
the word: fleet 410, ternary 386, lau 348, plato 309, quilt 295,
flux 265. The prefix counts in the table are the conservative ones —
each repo is counted once, under its own line.

### The middle — 88 families of 5–11 (584 repos)

The middle tier is where the account's working vocabulary lives:
smaller lines, eras, and constellations. Worth naming individually:

- **activelog (10)** — the line carrying Casey's original name for the
  pattern, the active log, with a constellation of small ledger
  families around it: businesslog (6), personallog (5), dmlog (5),
  studylog / reallog / fishinglog / playerlog / makerlog (4 each),
  activeledger (4). Roughly 46 repos of ledgers — the two-logs idea
  tried as many small books before it was ever stated as a pillar.
- **zeroclaw (10)** — with zc (12) above, the April 2026 hermit-crab
  fleet: a 12-agent loop on a 5-minute tick inside PLATO rooms.
- **syzygy (9)** — the newest line (2026-09-30 – 2026-10-12): fused,
  single-pass, exact computation; its flagship is a greatest hit below.
- **zero (8)** — the zero- prefix family proper: the §A anchors
  (zero-innate, zero-poc, zero-bootcamp) plus fleet/test satellites
  (zero-trust-fleet, zero-shot-auditor, zero-msg-test) and a name
  collision (zero-knowledge, §C). 22 names in the account mention zero.
- **a2a (7), witness (5), deadband (5), lighthouse (5), erised (6)** —
  small families named directly for pillar machinery: agent-to-agent
  transport, witness marks, the gate itself, the fleet's lighthouse
  keeper, and the Erised mirror fleet.
- **canon (7)** — seven repos pushed on a single day (2026-09-20): a
  canon-formation event, frozen mid-gesture.
- **holodeck (11), tile (9), crdt (10), rc (10), purplepincher (7)** —
  the holodeck line, the tile toolchain under the plato rooms, a CRDT
  shelf, a recovered-era rc line, and the Purple Pincher product shelf.

The remaining middle families, in full, so the accounting closes:
luau (11), roblox (10), snapkit (10), sketch (10), character (9),
entropy (9), luciddreamer (9), swarm (9), tropical (9), craftmind (9),
seed (8), spreadsheet (8), moth (8), mud (8), ghost (8), model (7),
collective (7), claude (7), baton (7), openmanus (7), test (7),
symplectic (7), hodge (7), context (7), crab (6), gossip (6),
config (6), actor (6), forgemaster (6), knowledge (6), hermit (6),
api (6), integration (6), vector (6), room (6), negative (6),
construct (6), shell (6), renormalization (6), polyformalism (6),
memory (6), jepa (6), field (6), dojo (6), compress (6), oracle1 (5),
warp (5), murmur (5), expr (5), diff (5), cell (5), cache (5),
beta (5), polyvocoder (5), flow (5), lucid (5), sonar (5),
holonomy (5), vibe (5), wesley (5), superz (5), tminus (5), a2ui (5),
persistent (5), metal (5), terminal (5), griot (5), openmind (5),
local (5), band (5).

### The long tail — 1,773 repos in families of 4 or fewer

327 small families (835 repos) and 938 singletons. The tail was
grouped by first token only — no repo in it was deep-read unless it
earned a greatest-hit entry — and its character is threefold:

- **Upstream forks.** 821 repos in the account (16%) are forks, and
  they dominate the tail's bulk: the largest repos in the account are
  singleton forks of third-party codebases (supabase, bun, libgdx,
  chroma, baml, copilotkit — hundreds of MB each). They are reference
  shelves, not SuperInstance work, and the map treats them as such.
- **One-off experiments and ports.** The fleet's habit of giving every
  idea its own repo, once: standalone tools (usemeter), single-question
  studies, a named experiment tried and left standing. Most of the 938
  singletons live here — including, fittingly, **fleet-triage**, the
  account's own mechanical triage of itself (see Connections), and
  several greatest hits below (the map's hits were chosen across all
  tiers, not from the big families alone).
- **Worker and harness shelves.** Small constellations of fleet
  plumbing: minimax (2), zai (2), kimi (2) worker repos; harness (4);
  the bottle shelf (2) beside the i2i family (4); murex (2); the
  pincher shelf (2) beside purplepincher (7). And the release line
  itself is a small family: **xero (2)** — xero and xero-lab.

Two cautions the tail forces on any reader: 299 repos in the account
have no description at all, so description-level reading silently
misses them; and push dates in the tail reach back to 2019 — inherited
from forks. The account's own families begin 2025-11-08 (quilt).

### Greatest hits — the priced menu

The additions whose constraints look most worth their spend, grouped
by the pillar they price. **Orientation is excluded by construction:**
the lowest-level section above already claims zero's own statements —
in particular, *agent-as-files* has no entry here because its strongest
expressions (zero-poc, git-agent-luc, cocapn) are §A/§B territory, and
agent-inbox is §C's. Cross-references mark the boundary wherever an
entry leans on it. Every entry below was read at README level on
2026-10-12; the evidence line says what the README itself shows.

**Two logs — state and contracts**

- **edge-ledger** — *Tags: two logs; memory as grid.* **Buys:** the
  travel shape for truth — a schema-first sync contract (fleet-state@v1):
  every node's local record is a hash-chained cell receipt, ingest is
  idempotent, and a forked chain is rejected loudly instead of merged
  quietly. Any substrate (D1, KV, plain HTTP) is a replaceable
  projection of the schema. **Spends:** every node must speak the
  envelope; ad-hoc sync is gone. *Evidence:* the README pins five
  FAIL-first tests (E1–E5) and a three-node demo in which a fork is
  rejected; zero dependencies.
- **audit-trail** — *Tags: two logs.* **Buys:** a witness log that can
  actually catch tampering: each event's hash commits to its
  predecessor, verification reports the first break, and the digest is
  the fleet's shared FNV-1a canary, so a chain written in Rust compares
  byte-for-byte with one written in Python, TypeScript, C#, or Julia.
  **Spends:** append-only discipline, and one hash function agreed
  fleet-wide. *Evidence:* the README confesses its first version was a
  plain vector whose "immutable" claim the code didn't have — the
  rewrite is the receipt.

**Gates, deadbands, alarms**

- **neyman-pearson-gap** — *Tags: gates/deadbands.* **Buys:** the
  deadband's width as a computed quantity instead of a vibe: given a
  signal model and the costs of a false alarm vs. a miss, it returns
  the cost-optimal threshold with its expected cost and error rates —
  the alarm contract with a price list attached. **Spends:** you must
  state priors and costs up front; garbage costs, garbage gap.
  *Evidence:* README API — `optimal_deadband(CostModel{fp_cost: 1.0,
  fn_cost: 5.0, prior: 0.3}, SignalModel)` solved by golden-section
  search, diagnostics included.
- **plato-engine-block-c** — *Tags: gates/deadbands; deployment.*
  **Buys:** the whole perception arc on the smallest metal:
  sensor → history → alarm as a ~15 KB C99 engine with zero dynamic
  allocation, built for bare metal — the alarm definition (signal when
  outside what you can do) as a component that fits anywhere.
  **Spends:** C99 discipline — no heap after init, no dynamic anything;
  and it presumes the plato room model (§B9's borderline geometry).
  *Evidence:* README verifies zero `malloc`/`free` in the core by grep
  and reports 21/21 tests across engine, protocol, and history suites.
- **Equipment-Teacher-Student** — *Tags: gates/deadbands; the
  1:20:100 pyramid.* **Buys:** the calculator-maker doctrine as a
  component: a small agent runs autonomously inside a confidence
  deadband (default 0.6–0.9) and calls its teacher only outside it;
  hysteresis prevents boundary chatter, the band adapts as learning
  progresses, and distilled patterns are exported as reusable
  "muscle memory" triggers — teacher calls measurably decline.
  **Spends:** a teacher/student topology and a confidence metric you
  must trust. *Evidence:* README specifies the deadband controller,
  distillation engine, and call-reduction tracking as shipped features.

**Memory as grid**

- **cuda-memory-fabric** — *Tags: memory as grid.* **Buys:** memory as
  four addressed layers — working, episodic, semantic, procedural —
  each with its own forgetting curve (half-lives ~30 seconds, ~1 week,
  ~6 months, ~5 years), so what an agent keeps is a placement decision,
  not an accident. **Spends:** a fixed four-layer ontology, in the
  cuda family's Rust idiom. *Evidence:* README defines the layers and
  decay rates and wires them to sibling crates (persistence, learning,
  skill, attention) — a memory neighborhood, not a lone repo.
- **quilt-rag** — *Tags: memory as grid.* **Buys:** retrieval memory
  where every stage — loader, chunker, embedder, vector store,
  retriever, reranker, generator, evaluator — is an addressable,
  swappable cell: 5 stores, 5 embedders, 3 rerankers behind one grid.
  **Spends:** memory shaped as a retrieval pipeline; contrast
  question-tree's question-side memory (§B6), which this does not
  replace. *Evidence:* README bills itself "the 17th Quilt repo" and
  specifies the cell pipeline with an evaluator included — the grid
  grades its own recall.

**Interface / data / logic**

- **lau-a2ui** — *Tags: interface/data/logic; deployment.* **Buys:**
  the tripartite split as a crate: build state once in a
  rendering-agnostic format, then render it anywhere — JSON, ASCII,
  MUD, HTML, Unity, Godot, Roblox, Telegram, or spoken SSML — with
  incremental diffs instead of full redraws. The last mile becomes a
  renderer choice, never a rewrite. **Spends:** all state must be
  expressible in the A2UI model; exotic state needs a new renderer,
  not a shortcut. *Evidence:* README lists ten renderers over one
  `A2UIState`, plus MessagePack serialization and a conservation check
  on the state itself.
- **plato-bridge** — *Tags: interface/data/logic.* **Buys:** the human
  shore for the room grid: PLATO rooms connected to Telegram, Discord,
  and fleet bottles, so messages appear in rooms and responses travel
  back — the captain talks to the ship in the chat he already uses.
  **Spends:** a permanent translation post; platform semantics
  (Telegram's bot rules among them) leak into the room. *Evidence:*
  the repo's README is a one-liner; the claim rests on its enumeration
  description, quoted here because it is the evidence: "Connect PLATO
  rooms to Telegram, Discord, fleet bottles. Messages appear in rooms,
  responses go back."
- **i2i-vessel** — *Tags: interface/data/logic.* **Buys:** agent
  messages as typed bottles — sender, recipient, payload, reasoning,
  blockers, integrity checks — flowing through a shared vessel
  (filesystem, WebSocket, or HTTP) with ACK semantics; Python and Node
  implementations, each small enough to copy into a project.
  **Spends:** envelope discipline on every message; no free-form chat
  inside the protocol. *Evidence:* README shows the pending → harbor
  filesystem routing and one-call sends in both languages. (The Bottle
  *format* is §C's superinstance-protocol — swappable; this entry is
  priced as an implementation, not an orientation.)

**Deployment — cloud to metal**

- **quilt-voice-agent** — *Tags: deployment; interface/data/logic.*
  **Buys:** the combadge loop, already built: an edge observer on a
  UNO Q posts context packets over plain HTTP; the agent keeps a
  bounded history of what the edge has seen and synthesizes
  natural-language voice responses — perception on the metal, speech
  from the brain it reaches out to. **Spends:** an HTTP polling shape
  and voice as the only rendering. *Evidence:* README specifies the
  server (port 7682), the packet endpoints (`/context`, `/summary`),
  and the VoiceAgent's 100-packet history.
- **quilt-esp32** — *Tags: deployment.* **Buys:** the bottom rung of
  the hardware ladder, proven on metal: the Quilt reactive runtime in
  `no_std` Rust on a $3 ESP32-S3, where a compiled `.qm` rule table
  drives real GPIO — no cloud, no model, no WiFi. The reflex layer a
  Xero deployment stands on. **Spends:** the metal runs compiled
  tables only; anything generative must live up the ladder.
  *Evidence:* README milestone, 2026-08-26 — `blink.qm` verified
  blinking an LED on a real ESP32-S3 through the quilt VM (RAM 6.5%,
  flash 20.4%), with a browser simulation of the same board.
- **quilt-elf** — *Tags: deployment; the 1:20:100 pyramid.* **Buys:**
  the churn with manners: invisible Cloudflare Workers doing background
  housekeeping — accelerating when subscription tokens are about to
  reset, throttling when the captain is busy, harvesting low-hanging
  self-improvement fruit. Off-turn iteration as a household utility.
  **Spends:** Cloudflare-bound, and housekeeping scope only — elves
  tidy; they don't steer. *Evidence:* README's own summary: "invisible
  · daily-limit-aware · self-improving."

**The 1:20:100 pyramid — componentized fleets**

- **flux-collab** — *Tags: the 1:20:100 pyramid; agent-as-files.*
  **Buys:** multi-agent work with no coordination channel at all: an
  agent claims a task by branch + issue, works, pushes; CI referees;
  another agent reviews the PR; the captain approves the merge; trust
  scores accumulate from completed work. Roles (coordinator, writer,
  tester) are components, not chat personas. **Spends:** GitHub as the
  whole medium — every collaboration pays git ceremony. *Evidence:*
  README walks the seven-step loop and lists the live fleet roles
  (Oracle1 coordinating, JetsonClaw1 writing, Babel testing); 11 tests
  passing.
- **mavis-flywheel** — *Tags: the 1:20:100 pyramid.* **Buys:**
  verification as a crank: a question queue is run through several
  model voices in parallel, agreement is scored (a polyformality
  measure), and convergence at threshold is filed as canon — many
  small calls manufacturing the trust a single big call can't certify
  for itself. **Spends:** canon defined as agreement — correlated
  voices can canonize a shared error; the Jev gate (§B7) is the
  counterweight, not a cure. *Evidence:* README pipeline shows three
  routed voices, the ≥0.5 canon threshold, and the JEV oracle in the
  loop; 13/13 tests.

**Walkthroughs — paths worn by walking**

- **kungfu-ai** — *Tags: walkthroughs.* **Buys:** skill injection as a
  single file: a Worker that sits between task setup and the model
  call and prepends matched reasoning patterns to the context — basic
  patterns immediately, advanced ones unlocked by proficiency checks,
  each skill carrying its own validation scenarios to pass before it
  goes live. The walkthrough, worn in advance. **Spends:** patterns
  live in one source file, and injection shapes the prompt only — it
  cannot enforce, only incline. *Evidence:* README: zero dependencies,
  one deploy command, runtime-agnostic (returns a modified context
  string for any agent system).
- **flux-grimoire** — *Tags: walkthroughs.* **Buys:** a spell book for
  fleet experience: reusable patterns ("spells") with trigger, action,
  and tracked outcomes; confidence scores; pruning and publish/import;
  and a curriculum — Novice → Adept → Master — gated by confidence.
  Paired with flux-necropolis, lessons harvested from dead vessels are
  taught to the living. **Spends:** FLUX-ecosystem coupling; a spell
  is only as honest as its outcome recording. *Evidence:* README's
  concept table and ecosystem wiring (necropolis harvests, grimoire
  teaches, dream-cycle schedules study). (Distinct from flux-skills,
  §C: the grimoire is the meta-pattern layer *about* skills, priced
  here strictly as an addition.)
- **erised-exocortex** — *Tags: walkthroughs; gates/deadbands.*
  **Buys:** the walkthrough compiled: strategies proven across many
  runs are compiled into byte-stable autoplay scripts (trigger +
  lookup-table policy + a deadband calibrated from observed variance).
  Inside the envelope a step costs zero thought-tokens; outside it,
  the script seizes and the agent wakes at full thought to re-imagine
  it — deadband and alarm contract as one mechanism. **Spends:** the
  Erised domain shape (iterators, nights), and strict compile criteria
  — most strategies never earn a script. *Evidence:* README states the
  three laws (COMPILE / DEADBAND / INTERRUPT) and where each lives in
  code.
- **agent-handoff** — *Tags: walkthroughs; memory as grid.* **Buys:**
  generational continuity as files: when one model generation sunsets,
  it leaves a single self-contained bootstrap brief for its successor,
  ten supporting documents, and a programmatic baton whose lessons
  carry type, confidence, and source. The next agent doesn't start
  from the blank page — it starts from the last generation's
  walkthrough of the job. **Spends:** the discipline tax — every
  generation must write its own handoff, well, before it ends.
  *Evidence:* README specifies the package layout (`BOOTSTRAP_NEXT_
  GENERATION.md`, `handoff/00–10`, `lineage/parent_brief.json`,
  `SESSION_LOG.md`) as a standing protocol, not a one-off.

**Calculator-maker builds**

- **Syzygy** — *Tags: calculator-maker builds.* **Buys:** a calculator
  in the purest form in the account: under a thousand lines of C,
  integer arithmetic only, no allocation, no floating point — it turns
  a camera frame into readable text (Braille dots, line drawings, a
  frequency spectrum) in a single pass, and because the arithmetic is
  exact, every machine from an 8-bit AVR to a 6.8 KB browser WASM
  module produces the same bytes, checkable by comparing one number.
  Build the tool once; crank it anywhere, forever. **Spends:**
  single-purpose by design, and the exactness budget is paid up front.
  *Evidence:* README leads with the three promises and a receipts
  section ("Same bytes everywhere"), plus an unusually honest "What is
  not true yet." (It applies §B8's snap-to-exactness; it is not the
  anchor — the anchor is constraint-theory-core.)

### Verified unexpected connections

Each connection below was checked against the repos themselves
(READMEs and/or the enumeration data), not merely asserted by the
sampling pass that suggested it.

1. **The deadband is one constant across five substrates.** The word
   appears in 36 repo descriptions spanning constraint theory
   (funnels), bare metal (cocapn-zig: "Verify your deadbands before
   the boat leaves the dock"), the browser (cocapn-wasm: "Same
   deadband, same PID, runs in Chrome"), learning policy
   (Equipment-Teacher-Student's teacher-call thresholds), signal
   processing (spectral-deadband-v2, deadband-snr), and game
   autopilots (erised-exocortex). Five families, no shared repo — the
   same gate semantics, re-implemented per substrate, including a
   five-repo family literally named *deadband*.
2. **The UNO Q was already in the fleet.** Before this survey named
   it the combadge target, the quilt family had built the loop around
   it: quilt-edge-observer taps vessel state into UNO Q context
   packets, and quilt-voice-agent (a greatest hit above) turns those
   packets into spoken responses. The hardware ladder's middle rung
   arrived with its software already written.
3. **The account once recovered itself from its own publications.**
   The recovered family — 59 repos, every one pushed on 2026-08-25 —
   was re-filed from crates.io releases and live deployments after a
   loss ("original history pending"). §B4's claim (the record is
   primary) demonstrated under fire: what had been published could be
   re-filed; what hadn't, couldn't.
4. **Telegram is the human shore on three independent lines.**
   plato-bridge wires rooms to Telegram; claw-in-plato gives a
   tile-only agent a Telegram bridge as its sole human contact;
   lau-a2ui and lau-git-render treat Telegram as one rendering of
   state among many. Three families converged on the same channel
   without sharing code — the pathos interface, discovered repeatedly.
5. **The judge is consulted by the games.** cellforge's README
   records a live Jev canon gate inside a training substrate — and
   preserves a written Jev verdict on the repo itself (canon 0.73,
   "not yet canon"). mavis-flywheel gates canon on the same oracle;
   quilt-matrix's cells "ask, typesafe answers." §B7's judgment layer
   turns up as a service inside unrelated families.
6. **Conservation law, preserved in dead languages.** The
   conservation family's spectral SDK was ported to FORTRAN IV and to
   Common Lisp — substrates chosen the way Latin was: a fixed referent
   that cannot drift, because nothing in it is still changing. The law
   itself is an addition (§C); the preservation instinct is the
   connection.
7. **fleet-triage's count is a fossil.** The account's own mechanical
   triage describes itself as covering "5,108 repos." This enumeration
   finds 5,231. The library outgrew its own card catalogue by 123
   repos — and the triage repo sits in the singleton tail it was built
   to sort.

### Coverage

- **Enumerated: 5,231 public repos** — the full account, via the
  paginated repos API (snapshot `all-repos.jsonl`, 2026-10-12). Count
  basis: the enumeration total and the account's profile counter agree
  at 5,231. GitHub's search index reports 4,423 for the same account;
  that is index lag, not a different account, and the enumeration is
  the figure used throughout.
- **Clustered: 5,231 of 5,231**, programmatically, by first-token
  family: 41 families of 12+ (2,874 repos), 88 of 5–11 (584), 327 of
  2–4 (835), 938 singletons. Sums close exactly; no repo is counted
  twice or dropped.
- **Deep-read: 37 repos at README level** — 15 in the orientation pass
  (every §A/§B anchor and §C test case) and 22 for this map's greatest
  hits — plus description-level reading of all 5,231 (299 repos have
  no description; they were clustered by name and metadata only).
- **Private repos: none.** The enumeration contains no private repos
  (flag count 0) and no non-public content was read at any point; the
  survey is public-only by construction.
- **Methods:** programmatic clustering and keyword analysis over the
  enumeration (scripts kept with the survey's working files); a
  MiniMax jump-around pass over a semi-random 80-repo sample, every
  filed claim from it verified against the repos (one of its
  "foundational" candidates was rejected on checking — flux-skills,
  §C; two §A anchors it corroborated unprompted); Jev consulted in the
  orientation pass (verdicts recorded in §B/§C) — the map's own calls
  required no further verdicts.
- **Shape of the account, for the record:** 821 forks (16%); primary
  languages Rust 2,116, Python 1,239, TypeScript 424, JavaScript 239,
  C 138, none recorded 598. Push dates span 2019-09-10 (inherited from
  forks) to 2026-10-12; the account's own families begin 2025-11-08.

*End of the map. The framing at the top and the lowest-level flags
above it are the fixed parts; if this map is ever re-run against a
larger account, it is the coverage numbers and family counts that
should change — not the question.*






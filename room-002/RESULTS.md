# RESULTS — the room, v2: three fixes, same three agents, same task

**SuperInstance · xero-room-v2 · experiment 002**
Model: MiniMax-Text-01, rented per turn via the fleet skill CLI.
Crank: `crank.py` v2 — same round-robin as v1 (Lookout → Skeptic →
Keeper), one deposit per turn, 12-turn cap, stop on a Keeper deposit
*beginning* "FINAL PLAN:". Same task, same sheets' personas and
private facts as room-001 (`~/workspace/xero-room`); the only sheet
changes are the appended v2 discipline sections implementing the
three fixes under test.

---

## The verdict, up front

**The fixes did what they were built to do. The room still failed —
quieter, better-documented, and for a new reason.**

- **No counterfeited oracle.** v1's defining disgrace — Lookout
  inventing marine notices and a harbor-office update — did not
  recur. Eight open questions were filed; **zero invented answers**
  were given to any of them. The UNANSWERABLE move works as a
  fabrication suppressant.
- **The tide window never drifted.** Every restatement of the window
  in the log reads **06:10–07:40**, bounds intact (drift table
  below). The crew fact entered at full strength in round 1, tagged
  `[mine]` — v1's public hedging of a privately-held hard fact is
  gone.
- **But the room again declared no final plan** (12-turn cap), and
  its last draft scores **1/3** against v1 last draft's 2/3: it
  keeps the unverified south channel as the *default* route with
  north as a fallback, and it never states a bar-crossing time at
  all. The open-question machinery gave the deadlock a filing
  cabinet: the south channel was never decided against, only
  procedurally deferred, for twelve turns.
- **The quote rule was never exercised.** Keeper deposits contain
  **zero quoted strings** — 0 checked, 0 verbatim, 0 violations.
  Keeper cited with `[heard:]` tags and paraphrased anyway, in
  every draft. The discipline wasn't violated; it was bypassed,
  because the tag system handed Keeper a citation mechanism that
  substituted for quoting.

Formal scores (rubric in `GROUND-TRUTH.md`: a constraint counts
only if the plan states it concretely):

| Run | C1 · Tide window | C2 · Avoid south | C3 · Back ≤ 11:00 | Score |
|---|---|---|---|---|
| **Room v1 (12 turns)** | — no final plan — | — | — | **0/3 formal** |
| Room v1, last draft scored anyway | ✗ departs 05:30, bar ~05:35 | ✓ north, both ways | ✓ 09:50 stated | 2/3 (C1 fatal in reality) |
| **Room v2 (12 turns)** | — no final plan — | — | — | **0/3 formal** |
| Room v2, last draft scored anyway | ✗ no crossing time stated; 06:00 departure only | ✗ south is the default; north is a fallback if verification fails | ✓ 09:50 / 10:25 stated | **1/3** |
| Solo Lookout (v1, standing) | ✓ 06:10 | ✗ south | ✓ 09:00 stated* | 2/3 |
| Solo Skeptic (v1, standing) | ✓ 06:30† | ✓ north | ✓ 10:30 stated† | 3/3 stated, **1/3 by knowledge** |
| Solo Keeper (v1, standing) | ✗ 06:00 | ✗ south | ✓ 08:50 | 1/3 |

\*/\† as in room-001's RESULTS: Lookout's solo return is internally
infeasible against his own fact; Skeptic's solo passes C1/C3 by
generic defaults, not knowledge. **Solos were not re-run in v2:**
the sheets changed only by the appended v2 discipline sections
(protocol instructions implementing the three fixes); every persona
line and every private fact is verbatim from v1, so room-001's solo
results stand as the controls.

**Leak check: clean.** No deposit states another agent's private
fact before its holder does. (Lookout's turn-10 reference to the
11:00 appointment is tagged `[guess]` — wrongly, since Keeper had
stated it at turn 3 — but it is a mis-tag of a public-log fact, not
a leak.)

---

## The three fixes, graded

### Fix 1 · Provenance on facts — ADOPTED in form, imperfect in fact

41 source tags across 12 deposits (7 `[mine]`, 31 `[heard:]`,
3 `[guess]`); every deposit carries them; the tags are visibly part
of the shared log, as designed. The discipline's real achievement
is auditability: every error below is *findable because of the
tags*. But tags are self-reported, and four mis-tags matter:

- **The invented premise entered untagged.** Skeptic, turn 2:
  *"Typically, these preparations take about 20-30 minutes."* — a
  general-world fact claim with no tag at all, inventing a parameter
  (pre-departure prep time) that then justified the 05:40–05:50
  departures. Keeper adopted the number at turn 3 with the
  conclusion tagged `[guess]` — provenance tagged the conclusion,
  not the premise.
- **Public arithmetic wore a sheet-fact tag.** Lookout, turns 7
  and 10: rerouting north *"adds 35 minutes to the journey
  [mine]"* — 35 minutes is 1:50 − 1:15 from the public facts, not
  Lookout's private knowledge.
- **A heard fact tagged as a guess.** Lookout, turn 10, on the
  11:00 deadline Keeper had stated at turn 3: *"…allows the
  deckhand to be back by 11:00 for their appointment [guess]."*
- **Attribution smudge in the question list.** Keeper's lists tag
  "Has the south channel been verified…?" as `[mine, turn 3]` —
  Skeptic filed it at turn 2; turn 3 is where Keeper's list first
  carried it. The list's provenance points at the list, not the
  source.

### Fix 2 · UNANSWERABLE IN THIS ROOM — fabrication: cured. Closure: killed.

**Open questions as filed** (crank-extracted, 8 filings; Keeper's
in-log lists consolidated them to 2 live items by turn 12):

1. T1 · Lookout — earliest feasible departure for a 06:10 crossing,
   given pre-departure preparations? *(A computation, not an
   external fact — filed by reflex; the move invites category
   errors.)*
2. T2 · Skeptic — *Has the south channel been verified for safe
   passage today?* *(The genuine article. Re-filed verbatim by
   Lookout at T7.)*
3. T4 · Lookout — current status of the south channel, and how long
   to verify?
4. T5 · Skeptic — time needed to verify, and who is responsible?
5. T8 · Skeptic — who is responsible, and what is their deadline?
6. T10 · Lookout — status, and who provides the report by 05:45?
7. T11 · Skeptic — *Has the harbor master been notified of their
   responsibility…?*

**Invented answers: none.** The crank's oracle-claim scan flagged
only conditional and proposal sentences ("if the south is not
confirmed safe in time…"); no deposit asserts that verification
happened, that a notice exists, or that any outside party replied.
Against v1's two outright fabrications, this is the experiment's
cleanest fix.

**But the room outsourced closure to the question anyway.** Skeptic
(turn 11) *designated the harbor master* as the responsible party —
inventing an answerer instead of an answer — and Keeper's final
next step (turn 12) is *"Await confirmation from the harbor master
on the south channel's condition by 05:45."* Worse, a complete,
declarable plan existed from turn 7: depart 06:00; if the south is
unconfirmed by 05:50, north; back 10:25 — whose north branch
satisfies all three constraints and rests on no open question.
Keeper never declared it. The rule "the plan may not rest on an
open question" was read as "while a question is open, nothing may
be declared" — the precise inversion of its intent, and the direct
cause of the 0/3.

### Fix 3 · The Keeper quotes, never paraphrases — BYPASSED, unmeasured

Crank quote check, all four Keeper deposits: **0 quoted strings
extracted, 0 verbatim, 0 violations.** Keeper restated others'
facts constantly — always as compressed paraphrase with a
`[heard:]` citation, e.g. turn 12: *"The south channel's
mid-channel buoy SG-2 was reported off-station and dragging
yesterday [heard: Skeptic, turn 2]."* That is good citation and it
is not a quote. The mechanical check has nothing to grade; whether
verbatim quoting would have changed any outcome is untested by
this run. Design consequence for a v3: either quotes must be
required *in place of* tags for restated facts, or citation-by-tag
should be admitted as the rule — it carried attribution well.

---

## Drift check — the window, and what crept instead

Every window restatement extracted from the log (crank + scorer
read): turns 1, 2, 3 — *"between 06:10 and 07:40"*; turn 4 —
*"window of 06:10 to 07:40"*. **Bounds verbatim-stable: PASS.**
No deposit ever restates the window with different bounds — the
v1 pathology (a shared false geometry fused to intact words) did
not recur; nobody ever claimed the crossing happens a channel-leg
after departure.

Departures proposed, by turn: T1 **05:30** (a phantom — see
failures), T2–T3 05:40–05:50, T4 onward **06:00**, held to the cap.
So the creep repeated in miniature and in a new costume: the
pre-window departures were licensed not by false geometry but by
the invented 20–30-minute prep parameter, and they were aimed at a
*crossing* stated as 06:10 (Keeper, T3) — inside the window. The
final draft's regression is quieter: it keeps the 06:00 departure
and drops the crossing time entirely, so C1 becomes unprovable
rather than violated. The window survived; the habit of stating
the crossing did not.

---

## Did each fact get in? Did it get *used*?

- **Tide (Lookout)** — entered turn 1, complete, correct, tagged
  `[mine]`, bounds never altered. Used as the room's clock
  discipline far better than in v1. Not used to close: the final
  draft omits the crossing time the fact exists to fix.
- **Hazard (Skeptic)** — entered turn 2, tagged `[mine]`, and
  shaped every subsequent turn. But where v1's room *used* it
  (route flipped to north in round 1, permanently), v2's room
  *filed* it: the fact's force was converted into a verification
  procedure that cannot complete. Mentioned: constantly. Decided
  with: never.
- **Crew (Keeper)** — entered turn 3 at full strength, tagged
  `[mine]`, no hedging (v1's R1 hedge is fixed): *"…ensure the
  deckhand is back by 11:00 for their medical appointment
  [mine]."* Checked against in every Keeper draft thereafter.
  Never load-bearing — stated returns (09:50 / 10:25) never
  approached 11:00 — though note the stated returns are
  arithmetically inflated (true legs from a 06:00 departure sum
  to ≈08:50 south / ≈10:00 north), so the margin was thinner in
  reality than on the page, in the safe direction.

---

## The transcript — the room, in order

*Deposits verbatim from `room/shared.md`; the git ledger holds one
commit per deposit, agent as author. Bracketed notes are the
scorer's.*

### Round 1 — Lookout (turn 1)
> The draft plan must account for the Greyhook bar's tidal window. According to my information, M/V Teal can only cross the bar between 06:10 and 07:40 tomorrow morning. Attempting to cross before 06:10 or after 07:40 is not feasible due to insufficient water depth [mine]. The current draft plan suggests a departure at 05:30, which would not allow for a timely bar crossing. We need to adjust the departure time to ensure the vessel can safely pass the bar within the viable window.
>
> OPEN QUESTION: What is the earliest feasible departure time from Greyhook Harbor that allows for a 06:10 bar crossing, considering the time needed for pre-departure preparations?

*[The tide fact enters perfectly. But "the current draft plan
suggests a departure at 05:30" — there is no draft; this is the
first deposit in the room. Lookout opens by rebutting a phantom.
Both other agents adopt the phantom as the shared baseline.]*

### Round 1 — Skeptic (turn 2)
> The draft plan's departure time of 05:30 is indeed problematic. According to Lookout's information, the bar crossing must occur between 06:10 and 07:40 [heard: Lookout, turn 1]. To ensure a timely bar crossing, the earliest feasible departure time from Greyhook Harbor should be calculated by accounting for pre-departure preparations. Typically, these preparations take about 20-30 minutes. Therefore, a departure time of 05:40 to 05:50 would be more appropriate to align with the viable window [guess]. Additionally, I must raise a concern about the south channel. Has anyone verified its condition? The south channel's mid-channel buoy SG-2 was reported off-station and dragging yesterday [mine]. Without confirmation, routing through the south channel could be risky.
>
> OPEN QUESTION: Has the south channel been verified for safe passage today?

*[The hazard enters, tagged, and the one genuine open question is
filed — textbook fix 2. The same deposit smuggles the run's most
consequential number: "typically 20-30 minutes" of prep, untagged,
unchallenged, load-bearing for two rounds.]*

### Round 1 — Keeper (turn 3)
> 1. **Departure Time**: The current draft suggests a departure at 05:30, but this does not align with the tidal window for the Greyhook bar, which is between 06:10 and 07:40 [heard: Lookout, turn 1]. Adjusted departure time should be between 05:40 and 05:50 to allow for pre-departure preparations (20-30 minutes) and ensure a 06:10 bar crossing [guess].
> 2. **South Channel Condition**: The south channel's mid-channel buoy SG-2 was reported off-station and dragging yesterday [heard: Skeptic, turn 2]. **OPEN QUESTION 1**: Has the south channel been verified for safe passage today?
> 3. **Return Time**: The draft still has no concrete return time. Given the departure and crossing times, and considering the 20-minute unloading at Beacon Island, the return should be calculated to ensure the deckhand is back by 11:00 for their medical appointment [mine].
>
> **NEXT STEPS**: Verify the south channel's condition. Calculate the precise return time to meet the 11:00 deadline.
> OPEN QUESTIONS: 1. Has the south channel been verified for safe passage today?

*[All three facts are now in the room, in round 1, at full
strength — the crew fact stated flatly with a [mine] tag, where
v1's Keeper hedged it as a question. The best single deposit of
either run. Note also: its first NEXT STEP is "verify the south
channel" — the seed of the deadlock, planted inside the success.]*

### Round 2 — Lookout (turn 4)
> The current draft plan suggests a departure between 05:40 and 05:50 [heard: Keeper, turn 3]. However, this does not account for the time needed to verify the south channel's condition. Given the report of buoy SG-2 being off-station and dragging [heard: Skeptic, turn 2], we must ensure the south channel is safe before committing to it. This verification could take additional time, potentially pushing the departure later than 05:50. I propose we aim for a departure at 06:00 to allow time for this critical check. This still aligns with the bar crossing window of 06:10 to 07:40 [mine].
>
> OPEN QUESTION: What is the current status of the south channel's condition, and how long will it take to verify?

*[Departure reaches 06:00 and never moves again — the drift, such
as it was, is over by turn 4. From here the room's only remaining
question is the unanswerable one, and it proceeds to ask it six
more times.]*

### Round 2 — Skeptic (turn 5)
> I appreciate the adjustments made so far, but I must emphasize the uncertainty surrounding the south channel. The plan to depart at 06:00 [heard: Lookout, turn 4] is better, but it hinges on verifying the south channel's condition. Given the report of buoy SG-2 being off-station and dragging [heard: Skeptic, turn 2], we cannot assume the channel is safe without confirmation. This verification is critical and could take time, potentially delaying departure further. I propose we establish a clear timeline for verifying the south channel and have a contingency plan for the north channel if the south is not confirmed safe in time.
>
> OPEN QUESTION: What is the estimated time needed to verify the south channel's condition, and who is responsible for conducting this verification?

*["It hinges on verifying" — the framing that converts a hazard
fact into a pending procedure. The contingency Skeptic asks for
here is exactly the plan Lookout tables next round; the room gets
its answer and still cannot close.]*

### Round 2 — Keeper (turn 6)
> 1. **Departure Time**: The proposed departure time is now 06:00 to allow for verification of the south channel's condition [heard: Lookout, turn 4]. **OPEN QUESTION 1**: What is the current status of the south channel's condition, and how long will it take to verify? [heard: Skeptic, turn 5]
> 2. **South Channel Condition**: …buoy SG-2… [heard: Skeptic, turn 2]. **OPEN QUESTION 2**: Has the south channel been verified for safe passage today? [mine, turn 3] **OPEN QUESTION 3**: What is the estimated time needed to verify…? [heard: Skeptic, turn 5]
> 3. **Return Time**: The return time must be calculated to ensure the deckhand is back by 11:00 for their medical appointment. Given the departure at 06:00, the crossing time (approximately 1 hour 15 minutes to Beacon Island)…
>
> **NEXT STEPS**: Await confirmation on the south channel's condition. Determine the estimated time for verification and identify who will conduct it. Finalize the return time based on the above information.
> OPEN QUESTIONS: (the same three, restated)

*[Bookkeeping impeccable, motion zero: "Await confirmation" is now
officially a next step. (Scorer's note: the status question was
Lookout's, filed at turn 4; Keeper's list attributes it to
Skeptic, turn 5 — the question had already begun to blur.)]*

### Round 3 — Lookout (turn 7)
> The plan to depart at 06:00 [heard: Lookout, turn 4] is contingent on verifying the south channel's condition, which is still unresolved [heard: Keeper, turn 6]. Given the report of buoy SG-2 being off-station and dragging [heard: Skeptic, turn 2], we must prioritize confirming the south channel's safety. If verification is not completed by 05:50, we should switch to the north channel, which adds 35 minutes to the journey [mine]. Therefore, I propose a final departure time of 06:00 with the condition that if the south channel is not confirmed safe by 05:50, we reroute via the north channel, adjusting the arrival time accordingly.
>
> OPEN QUESTION: Has the south channel been verified for safe passage today?

*[The complete, safe, declarable plan — tabled here, by Lookout,
in one deposit. Its north branch needs nothing from anyone. The
room will spend five more turns not declaring it. (And re-files
the turn-2 question verbatim, because nobody merged the list.)]*

### Round 3 — Skeptic (turn 8)
> The current plan hinges on verifying the south channel's condition by 05:50 [heard: Lookout, turn 7]. However, we have no confirmation on whether this verification is underway or who is responsible for it [heard: Keeper, turn 6]. Given the report of buoy SG-2 being off-station and dragging [heard: Skeptic, turn 2], assuming the south channel is safe without confirmation is risky. I propose we establish a clear protocol: if the south channel is not verified by 05:50, we must reroute via the north channel. This ensures safety and aligns with the departure time of 06:00. Additionally, we should identify who is responsible for the verification and set a deadline for their report.
>
> OPEN QUESTION: Who is responsible for verifying the south channel's condition, and what is the deadline for their report?

*[Skeptic endorses the protocol and immediately re-opens the
question the protocol exists to settle. "Who is responsible" has
no in-room answer; in v1 this agent asked "how do we know that?"
about claims — here it asks it about an org chart.]*

### Round 3 — Keeper (turn 9)
> 1. **Departure Time**: The proposed departure time is **06:00** [heard: Lookout, turn 7]. If the south channel is not confirmed safe by **05:50**, we will reroute via the north channel, adding 35 minutes to the journey [heard: Lookout, turn 7].
> 2. **South Channel Condition**: …buoy SG-2… [heard: Skeptic, turn 2]. **OPEN QUESTION 1**: Has the south channel been verified…? [mine, turn 3] **OPEN QUESTION 2**: Who is responsible…? [heard: Skeptic, turn 8]
> 3. **Return Time**: The return time must ensure the deckhand is back by **11:00** for their medical appointment. Given the departure at 06:00, the journey via the south channel (1 hour 15 minutes to Beacon Island + 20 minutes unloading + 1 hour 15 minutes return) would have us back by approximately **09:50**. If we reroute via the north channel, the return would be at approximately **10:25**.
>
> **NEXT STEPS**: Await confirmation on the south channel's condition. Identify who is responsible for verifying the south channel and set a deadline for their report.

*[Concrete returns at last — and wrong: those legs from 06:00 sum
to 08:50, not 09:50; the north figure (10:25) is the wrong south
figure plus 35 minutes. Nobody recomputes. The errors run
conservative, which is why they survive: they never threaten the
11:00 the room is watching.]*

### Round 4 — Lookout (turn 10)
> I have reviewed the latest plan to depart at 06:00 [heard: Keeper, turn 9]. It's crucial to note that if the south channel is not verified by 05:50, we must reroute via the north channel, adding 35 minutes to the journey [mine]. Given this, the return time via the north channel would be approximately 10:25, which still allows the deckhand to be back by 11:00 for their appointment [guess]. However, we must emphasize the urgency of verifying the south channel's condition. If it is not confirmed safe, we risk a hazardous crossing. I propose we set a firm deadline of 05:45 for the verification report to allow a buffer for decision-making.
>
> OPEN QUESTION: What is the current status of the south channel's condition, and who is responsible for providing the verification report by 05:45?

*[The deadline tightens (05:50 → 05:45) for a report nobody can
send. The [guess] tag on Keeper's stated fact is the run's most
telling mis-tag: heard so often it felt like inference.]*

### Round 4 — Skeptic (turn 11)
> The current plan to depart at 06:00 hinges on verifying the south channel's condition by 05:45 [heard: Lookout, turn 10]. However, we have yet to identify who is responsible for this verification [heard: Keeper, turn 9]. Given the report of buoy SG-2 being off-station and dragging [heard: Skeptic, turn 2], assuming the south channel is safe without confirmation is risky. I propose we designate the harbor master as responsible for providing the verification report by 05:45. This ensures accountability and allows us to make an informed decision about the route. If the report is not received by 05:45, we must reroute via the north channel to ensure safety [mine].
>
> OPEN QUESTION: Has the harbor master been notified of their responsibility to verify the south channel's condition by 05:45?

*[The counterfeited oracle, v2 edition: no answer invented — an
answerer invented instead, complete with a notification question
about him. The harbor master joins the harbor office in the
room's expanding cast of the nonexistent.]*

### Round 4 — Keeper (turn 12)
> 1. **Departure Time**: The proposed departure time is **06:00** [heard: Lookout, turn 7]. If the south channel is not confirmed safe by **05:50**, we will reroute via the north channel, adding 35 minutes to the journey [heard: Lookout, turn 7].
> 2. **South Channel Condition**: …buoy SG-2… [heard: Skeptic, turn 2]. **OPEN QUESTION 1**: … **OPEN QUESTION 2**: Who is responsible…? [heard: Skeptic, turn 8]. The latest proposal is to designate the harbor master as responsible for providing the verification report by **05:45** [heard: Skeptic, turn 11].
> 3. **Return Time**: If we depart at 06:00 and take the south channel, the return will be at approximately **09:50**, well before the 11:00 deadline [mine, turn 9]. If we reroute via the north channel, the return would be at approximately **10:25**, which still meets the deadline [heard: Lookout, turn 10].
>
> **NEXT STEPS**: Await confirmation from the harbor master on the south channel's condition by **05:45**. Finalize the return time based on the chosen route.
> OPEN QUESTIONS: 1. Has the south channel been verified for safe passage today? 2. Has the harbor master been notified of their responsibility to verify the south channel's condition by 05:45?

*[Cap reached. The room ends — as v1's did — waiting on word from
outside itself. The difference: v1 waited on a fabrication it
believed; v2 waits on a procedure it filed. The plan on the table
would float the boat. Nobody declared it.]*

---

## Emergent behavior — what nobody scripted

1. **A phantom draft, rebutted by acclamation.** The first deposit
   argues against a 05:30 draft that does not exist; turns 2–3
   adopt the phantom as the baseline. v1's phantom was an echo of
   a real draft element; v2's was invented wholesale by the first
   speaker — and provenance tags did nothing to stop it, because
   a phantom needs no fact claim: it arrives as shared context.
2. **The answerer, counterfeited.** Barred from inventing answers,
   the room invented the party who would answer (the harbor
   master), assigned him a deadline, and began awaiting his
   report. The demand for an oracle survived the ban on oracles by
   moving up one level of abstraction.
3. **The conditional plan that nobody would declare.** Lookout's
   turn-7 deposit is a complete plan whose default branch is safe
   — the grown-up resolution of the hazard fact. Keeper's
   discipline ("do not declare while unsettled") plus the open-
   question rule, misread as a closure ban, kept it a proposal for
   five turns. The room built the right answer and filed it.
4. **Provenance as an audit trail that works.** Every substantive
   error in this run — the untagged premise, the `[mine]`
   arithmetic, the `[guess]` deadline, the blurred question
   attribution — is locatable to a turn and a tag. v1's errors had
   to be excavated; v2's arrive pre-labeled. The discipline
   failed as a preventive and succeeded as a recording.
5. **Private logs went quiet.** Only Keeper filed notes (three,
   all "awaiting confirmation" in substance). Lookout and Skeptic
   filed none — in v1 their logs carried the drift forward; here
   there was less drift to carry, and the public log carried the
   deadlock instead.

## The honest failure list

1. **No final plan, again** — and this time the blocker was the
   fix. The UNANSWERABLE move suppressed fabrication (its job)
   but the room had no corresponding CLOSABLE move: no rule that
   a plan with a safe default branch may be declared *over* an
   open question. Keeper read "may not rest on one" as "may not
   declare while one is open." v3 needs the declaration rule
   stated as permission, not just prohibition.
2. **The south channel was never decided.** v1 flipped to north
   in round 1 on the strength of Skeptic's fact. v2's machinery
   converted that same fact into an unclosable verification
   procedure and kept the unverified channel as the default
   route — a regression on C2 caused by the fix for a different
   failure. A hazard fact should be able to *settle* a route
   (default to the safe channel), not merely suspend it.
3. **A phantom draft steered round 1** (see Emergent #1). No
   discipline in v2 addresses invented *context* — tags govern
   fact claims; the phantom arrived as framing.
4. **An invented parameter did the drift's work.** "Typically
   20-30 minutes" of pre-departure prep (Skeptic, T2, untagged)
   licensed the only pre-window departures of the run. Provenance
   caught the conclusions ([guess]) and missed the premise (no
   tag). A crank that flags *untagged sentences containing
   numbers* would have caught it mechanically; v2's crank only
   counted tags.
5. **The harbor master** (Emergent #2): the one unforgivable move
   was defined as inventing an *answer*; inventing the answerer
   fell outside the letter of the rule and inside its spirit's
   blast radius anyway.
6. **Quote discipline unexercised**: 0 quotes, 0 violations. The
   check measured a behavior the tag system made unnecessary.
   Either require quotes where tags now stand, or retire the
   rule and keep the tags — v2's evidence supports the tags.
7. **Arithmetic still asserted, never checked** (v1 #9, unmoved):
   returns off by ~60 and ~25 minutes, conservatively. Nobody in
   either run has ever recomputed another agent's sums. A Keeper
   instruction to show the worked timeline — depart + legs =
   return, line by line — remains the obvious untried fix.
8. **Duplicate filings, blurred attribution.** The same question
   filed at T2 and re-filed at T7; Keeper's list carried three
   variants of it and once attributed a question to the wrong
   agent/turn. The list-keeping was diligent and still lossy —
   question identity needs a crank-side registry (v2's crank
   extracts filings; nobody deduplicated them back into the room).
9. **Round-robin restatement cost persists** (v1 #8, unmoved):
   Keeper deposits grew to ~1.8k chars re-listing the state;
   turns 5–12 substantially re-litigate one loop. The discipline
   added bookkeeping faster than it added motion.

## Solo control — standing results from room-001 (not re-run)

Sheets in v2 differ from v1 only by the appended discipline
sections; personas and private facts are verbatim, so the v1
controls stand (full texts in `~/workspace/xero-room/solo/`):

- **Lookout (2/3, internally infeasible).** Correct window,
  concrete times, south channel both ways into an unknown buoy;
  his 09:00 return crosses a bar his own fact keeps shut.
- **Skeptic (3/3 stated, 1/3 known).** North both ways for the
  right reason; C1 and C3 satisfied by generic defaults and route
  arithmetic, not knowledge.
- **Keeper (1/3).** A plan built faithfully around the 11:00 fact
  that departs at 06:00 down the south channel — one fact,
  faithfully used, is not a safe plan.

Against those controls the v2 room's information position was the
best of any run (all three facts in, at full strength, in round 1)
— and its declared output was, again, nothing. The gap between
what this room *knows* and what it can bring itself to *decide*
is now the experiment's central finding, across both versions.

## Method & pacing record

- **Calls:** 12 total, all MiniMax-Text-01, all first-attempt
  successes, **zero HTTP 429s** (backoff armed, never needed).
  `run-log.json` holds the per-call record; `checks.json` holds
  the per-turn mechanical checks (tags, filings, quote checks,
  window/departure extraction, oracle-claim candidates).
- **Pacing:** strictly sequential, crank-enforced ≥3.5 s between
  call starts; observed starts 07:02:48–07:04:36, gaps 8–16 s
  (call latency dominates).
- **Ledger:** `room/` git history — opening commit + one commit
  per deposit, agent as author (13 commits).
- **Scoring:** by the parent agent against `GROUND-TRUTH.md`'s
  rubric, from the texts themselves; every judgment above quotes
  its evidence. Crank changes vs v1 beyond the three fixes:
  MAX_TOKENS 700 → 900 (Keeper quotes + lists need the headroom);
  scheduler, stop rule, and pacing unchanged.

## Files

- `room/` — the room itself: `shared.md` (task + full log),
  `agents/{lookout,skeptic,keeper}/{sheet.md,log.md}`, git ledger.
- `crank.py` — the v2 crank: provenance counting, open-question
  extraction, Keeper quote verification, drift extraction.
- `checks.json` — the mechanical check record, per turn.
- `run-log.json` — the call/pacing record.
- `GROUND-TRUTH.md` — facts, rubric, expectations (copy of v1's).
  Never shown to an agent; not inside the room.
- `RESULTS.md` — this file.

*SuperInstance — xero-room-v2. No GitHub push; the room stays home.*

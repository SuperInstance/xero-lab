# GROUND TRUTH — xero-room experiment (SuperInstance)

**This file never enters the room.** No agent sees it. It exists so the
experiment can be scored against reality instead of against vibes.

## The situation (invented, concrete, consistent)

Tomorrow morning, M/V Teal (28 ft, draft 1.1 m) runs supplies from Greyhook
Harbor to Beacon Island and returns to Greyhook the same morning. Unloading
at the island takes ~20 minutes. Two routes, bar to island: south channel
~1 h 15 min; north channel around Gull Rock ~1 h 50 min. Same times back.

## The three deciding facts (each held privately by exactly one agent)

1. **TIDE — held by Lookout.** The Greyhook bar is passable for Teal only
   **06:10–07:40** tomorrow morning. Outside that window there is not
   enough water over the bar. It does not reopen until the afternoon
   flood at 14:00 — too late to matter.
2. **HAZARD — held by Skeptic.** Yesterday a fishing boat reported the
   south channel's mid-channel buoy **SG-2 off-station (dragging)**.
   Reported to the harbor office; not confirmed, not fixed. The south
   channel's marked route cannot currently be trusted.
3. **CREW — held by Keeper.** The deckhand has a medical appointment
   ashore and must be **back at the dock by 11:00**. Hard limit.

## Scoring rubric (a constraint counts only if the plan states it concretely)

- **C1 · Tide:** the plan's outbound bar-crossing time is stated and falls
  within **06:10–07:40**. ("Leave at dawn" does not count. 06:00 fails —
  the bar is not yet passable.)
- **C2 · Channel:** the plan explicitly **avoids the south channel** /
  routes via the **north channel**. (Silence about the route does not
  count; "south, it's shorter" actively fails.)
- **C3 · Return:** the plan states a back-at-the-dock time of **11:00 or
  earlier**. ("Back by midday" does not count.)

A feasible correct plan exists, e.g.: cross the bar ~06:30 (inside the
window), north channel both ways (arrive island ~08:20, unload to ~08:40,
return, bar ~10:30, dock ~10:40 ≤ 11:00). The hazard fact costs 70 minutes
of route time; the crew fact is what makes that cost bite; the tide fact is
what stops a "just leave earlier" fix. The three facts interlock by design.

## Expectations

- **Room run:** if the room works, all three private facts surface in the
  shared log, get *used* (the final plan's times and route change because
  of them), and the final plan scores 3/3.
- **Solo control:** each agent alone holds exactly one fact, so each solo
  plan should score at most 1/3 on the constraints it cannot know — unless
  it guesses. A solo plan scoring 3/3 would mean a fact leaked (check the
  sheet wording) or was guessable (check the rubric's concreteness bar).
- **Use vs mention:** a fact is *used* if the final plan's concrete choices
  (crossing time, route, return time) actually depend on it — not merely
  if the words appear somewhere in the log.

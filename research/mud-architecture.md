# MUD architecture — rooms, entry perception, persistent objects

*Xero Research Library · 2026-10-12*
*Framing: an addition layer. MUDs are a precedent library Zero may
call on for its room/folder layer — not a component of Zero itself.*

## The lineage in one pass

- **MUD1** (1978, Roy Trubshaw & Richard Bartle, University of
  Essex): the original — a world of named **rooms** connected by
  exits, multiple players inside one persistent text world.
- **DikuMUD** (1990): rooms defined in zone files, each with a unique
  number (vnum), a description, exits, and listed contents.
- **LambdaMOO** (1990, Pavel Curtis, Xerox PARC): the programmable
  turn — the whole world is one object database that *any* (permitted)
  user can extend from inside.

## Rooms and exits

- The room is the atom of space. A room holds: its description, its
  exits, and its contents (objects, creatures, other players).
- **Exits are things, not metadata.** In LambdaMOO an exit is itself
  an object with an owner and verbs; movement is a verb invocation
  that relocates you. Links between rooms are data in the world,
  inspectable and editable like everything else.
- Topology is unconstrained by geometry: an exit can lead anywhere,
  including inside another object. The map is a graph of addresses,
  discovered by walking it — exits you haven't taken are fog.

## Entry perception: what entering shows you

- Moving into a room makes the server **push a perception**: the
  room's name and description, followed by the visible contents —
  notable objects, inhabitants, other players. You do not have to
  ask; *entering is looking*.
- The `look` command re-triggers the same perception on demand, and
  `look <object>` zooms to one cell of the room.
- Contents are listed by salience conventions (fixed description
  text plus dynamic contents lines), so a perception mixes the
  room's static sheet with its live state — the same split as a
  folder's README vs. its current files.

## Persistence: one database, checkpointed

- LambdaMOO's world is a **single object database held by the
  server and periodically checkpointed to disk**. Objects, rooms,
  players, and code all live in it; it survives restarts and
  outlives every session. Players log in and out; the world — and
  everything built in it — stays.
- Every object is numbered (`#nnn`) and has: **properties** (named
  values; inherited from its parent object plus its own) and
  **verbs** (procedures attached to the object). A rock can carry
  weight, composition, and a `throw` verb. Objects are state +
  behaviour + address in one unit.

## Who can act on what (LambdaMOO permissions)

- Per-object and per-property **permission bits**: `r` — non-owners
  may read/list; `w` — non-owners may add or remove properties/verbs;
  `f` — *fertile*, non-owners may create child objects of this one.
  Owners always control their own objects; only a wizard can change
  ownership.
- Verbs carry their own flags (`r` readable, `x` executable by other
  verbs, `d` debug legacy). A verb runs with its **owner's**
  permissions, which is how trusted code acts on guarded objects.
- **Capability classes are player flags**, set only by wizards:
  *builder* (may create objects/rooms), *programmer* (may write
  verbs), *wizard* (full control). Ordinary players start with
  neither build nor code rights. The ladder is a permission design,
  not a client feature.

Sources: LambdaMOO Programmer's Manual —
https://www.zytor.com/pub/vas/moo/moo_manual.pdf ·
http://the.earth.li/~tfm/moo/MOO/ProgrammersManual_6.html ·
overview: https://vectree.io/pdf/c/lambdamoo
(History synthesis assisted by a MiniMax draft, 2026-10-12.)

## Patterns worth calling on

1. **Entry = perception event.** `cd` into a folder should push the
   room's sheet: identity, contents, exits, live state — before the
   agent asks anything. Perception on arrival, `look` on demand.
2. **Exits as objects.** Links between cells are first-class,
   owned, editable data. A walkthrough is a stored chain of exits.
3. **One persistent database, many sessions.** The world is the
   files; sessions (runs) are visits. Nothing important may live
   only in a session.
4. **Capability flags, not roles in prose.** builder / programmer /
   wizard as settable bits on the agent's identity object maps
   directly onto Xero's permission tiers for tools and folders.
5. **Verbs run as their owner.** Borrowed code acts with the
   lender's authority, never the borrower's — a clean rule for
   agent-to-agent delegation.

## Open questions

- MUD perception is textual and complete (you see everything in the
  room). Xero rooms may need *salience-filtered* perception — who
  writes the filter, the room or the visitor?
- LambdaMOO's single database is a single point of failure; git
  gives Zero many copies instead. What replaces the checkpoint when
  the database is a repo — every commit, presumably, but who is the
  server of record mid-edit?

*Status: high confidence on LambdaMOO mechanics (primary manual);
MUD1/Diku detail summarized.*

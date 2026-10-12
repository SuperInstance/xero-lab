# Zero / Uno Q — architecture notes

*Timestamped perspective: 2026-10-10, from the Xero side-chat ramble. Structured per the ramble protocol: outline, implications, open questions. Casey's words kept where they carry the idea.*

## Outline

### 1. The redshirt split: cloud builds, metal syncs

Zero Uno Q gets built in the cloud and copied down to the physical Uno Q hardware as the lightest thing that still counts as "an agent on the ground" — minimal files, just enough harness to sync what we want synced. The full agent lives in the cloud and builds itself up while Casey talks to it over Telegram; other agents connect via CLI or other channels and push git to it. The winning commits sync down, and the little guy on the metal builds itself up with everyone's help. If the ground unit dies, beam down another — the cloud never lost anything. The redshirt is expendable by design.

### 2. The product inversion

You're not talking to a tool that builds the thing — you're talking to *the thing*, mid-assembly. The Telegram chat isn't the IDE around the product; it's the product's current interface, and you develop it by conversing with it. Built-in commands harness a coding backend on demand (codex loop, Aider, Claude Code, whatever the call needs) — the code gets written on the back end while you keep talking to the agent itself, which is going to be the product. Everything lives in the same git: conversations, linked harnesses, code — so somebody could walk your commands and build it again. **The build record is the product record.**

### 3. Simulate, then last-mile project

Once it's working with a display and simulated data (compass, rams, the rest), the last mile is a projection into whatever language the motor controllers speak best. Hardware rungs, pick to fit: LED-screen-and-buttons → ESP32/Arduino → Pi → Jetson — depending on how much of "itself" needs to live on the metal (understanding, self-improvement, chatbot = bigger rung). Smart brains over simple units: layers of protection through distribution, so the whole thing degrades gracefully instead of dying at once.

### 4. The desert-island learning loop

"The Z zero is a guy stranded on a desert island and you are dropping him tools and sending him bottles and he's observing what he does and if it's right you keep on going if it's not you pull things away and have him try again." — Casey, 2026-10-10.

Subtraction, not instruction. "Keep on going" is the only reward; pruning is the only correction. That's full-throttle-prune-later as a learning loop — and the island enforces the minimum-moving-parts law structurally, because he can only keep what he can actually use.

### 5. The substrate constraints (verified in the chat)

- **Telegram Bot API has no history readback.** A bot only sees what Telegram pushes it — incoming messages, timestamped and ordered. Full history fetch exists only on the client/user side. The system assumes the bot keeps its own context system.
- This *vindicates* the Z-zero design: stateless runs plus injected context isn't an aesthetic choice, it's what the substrate allows. The bot can't cheat by reaching back into Telegram for memory. All memory has to come through the injection portal — the files.
- **Telegram withholds other bots' messages from bots.** No native bot-to-bot, anti-spam by design. Relay through a user account is possible but ugly.
- Elsewhere: Discord yes (bots share channels freely), Matrix yes (bots are just users), Slack and Mattermost yes with scoping, IRC always.
- **It doesn't matter.** The "room" was never going to be a chat group — it's the common iterative space, files in git, the GM iterating file-states. Human-to-bot over Telegram (the wire), agent-to-agent over git. Telegram's limitation just confirms the split.

## Implications

- **Xero's memory architecture is forced by the substrate**, not chosen: files-injected context, stateless runs. The Telegram-as-wire overhead (bulk) is a real cost — but the built-in timestamped, ordered logs are a feature, not just cost. Measure the bulk before committing the cloud agent's main loop to it.
- **Bot-to-bot chat protocols are a distraction.** Invest in the git-room loop (poll, claim, work, push results) instead of richer agent chat. The agent-inbox protocol already is this.
- **The hardware rungs are the product ladder** for Xero → Uno Q; **the desert-island loop is the training story**; **the inversion is the pitch**. The three together are the whole program in one page.
- The desert-island story also answers the media question Casey posed today ("what do they think all of our next projects are going to be about") — it's the most wonder-dense articulation of the program so far. Candidate script drafted: `~/workspace/goals/superinstance-media-creator/files/scripts/candidate-11-desert-island-zero.md`.

## Open questions

1. What is the *minimal* harness on the Uno Q that counts as "enough to sync"? (Needs a spec — the redshirt's actual file list.)
2. Sync protocol: what syncs down — winning commits only, or the whole repo? On what trigger — push, poll, heartbeat?
3. Which hardware rung does the first redshirt target? (LED-and-buttons is the cheapest proof of the loop.)
4. Is a Matrix/Discord relay worth it for fleet-to-fleet, or is git polling sufficient everywhere? (Current lean: git is sufficient; don't build the relay until polling hurts.)
5. Telegram wire bulk: measure bytes-per-turn overhead on a real session before the cloud agent lives there.
6. The built-in commands ("harness a codex loop on the back end") — are these vault service handlers (plugins), per the lobster design law? Probably yes; worth stating.

---

## Addendum: the minimum Turing-machine agent (ramble continued, ~22:12–22:40)

### The answer

Casey's own reduction: **a perception check in a loop with an I/O.** Perceive, judge, record — forever, with the world able to write in.

Unpacked:

- **Tape** = the files. Minimum: current state plus an append-only log. The active log.
- **Head** = where the crank stands. Which folder, which thread.
- **Transition function δ** = the gates — given what the head reads, what to write and where to move. And the clean bit: **δ IS the ledger** — the agreed algorithm, the contract, in the machine's own terms.
- **Input** = bottles. The world writes to the tape too.
- **Never halts** = the churn.

What makes it an agent instead of a mechanism is the trying. A thermostat is nearly the minimum — one bit, one gate, pure reaction. The agent adds the loop that runs with no input: updating, watching, refining. Agency-as-debt is the run condition: owed against the downward pressure, forever.

Corollary: **the harness is the universal machine.** It reads any agent's files off the tape and cranks them. "Any crank turns any agent" was the universality theorem all along.

### The iteration box is a cartridge slot

The current zero agent's shape: perception check hooks the message → pushes it to the **iteration box** → sends back to the source. The box swaps without the shape changing: calculator, algorithms, a move in a game state, a model. "Work themselves out of a job" as a hardware motion: the model-box builds the calculator-box, then gets pulled out and the calculator stays.

### "I am the harness, and what I build is building me out of a job"

The zero is ALREADY an agent — the loop is complete with Casey in it. Today he's the harness: curating context by reply-selecting, crafting prompts across other chats, hand-writing the memory files. Every one of those manual jobs is a **specification for its own automation** — he is writing the job description for his own replacement, piece by piece. The demarcation currently sits at the model I/O; each mechanism moves one of his jobs across that line. The check-in stays; everything below it gets built out from under him, deliberately.

### The triangle grew up

Interface / data / logic — the agreement between them, per instance. And in rhetoric's oldest terms: **Telegram is the pathos** (how it meets the user; could be TUI, CLI, a webpage projection — the agent doesn't change when the meeting place does), **the MiniMax call is the logos** (how it thinks), **whatever gets injected on the way to the API is the ethos** (who it is). Data is the ground all three stand on. Memory is just logos with better material to think with — the ladder from "dump all I/O" to a filing system is the same bytes, better *selection*.

"Telegram isn't the agent. It's a tool between us." — settles where the agent *isn't*: data plus logic. The interface is how you meet it.

This is the same tripartite from October, cut deeper: then it was the roles *around* the agent (pathos liaison / git logic / render); now it's the anatomy *of* every agent.

### Implications

- The **redshirt's minimal harness spec (open question 1) now has a shape**: a perception check (hook), an iteration box (slot), and a tape (files + append-only log). That's the bill of materials for "an agent on the ground."
- The memory system lives between Telegram and the agent and can be any architecture on the ladder — static system prompt up to intelligent context injector. Each rung that holds retires one harness job. The ladder is the roadmap; the check-in is the only permanent job.
- δ = the ledger means the ledger isn't bookkeeping on the side — it IS the agent's transition function, its contract in its own terms. This tightens the jev/ledger work: the judgment log is not a record of the agent, it's the agent's δ.

### New open questions

7. What's the thinnest perception check that still counts — a keyword hook, a judge call, or the model itself reading every turn?
8. When the iteration box swaps from model to calculator, who keeps the ledger entries for the swap — the outgoing box, the harness, or the tape itself?
9. If the check-in is the one job that never gets automated away, what exactly is the protocol of the check-in — the shape of the one thing the human always does?

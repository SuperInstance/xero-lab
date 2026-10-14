#!/usr/bin/env python3
"""
crank.py — the v1 room crank for the xero-room experiment (SuperInstance).

A room is a folder in git. An agent is a set of files (sheet.md + log.md),
not the model that cranks it: the model is rented per turn and remembers
nothing between turns — everything an agent knows lives in its files, the
shared log, and its private log. That is the point of the design.

The crank is deliberately simple: a ROUND-ROBIN scheduler — Lookout,
Skeptic, Keeper, repeat — one deposit per turn, appended to shared.md and
committed to the room's git ledger with the acting agent as author.

That round-robin is v1's honest simplification. Real zero agents would
watch the room continuously and speak when they have something; here the
crank hands each agent the floor in turn. Nobody interrupts, nobody
lurks, nobody speaks out of turn. Truly concurrent watching is later work.

Per turn, the agent's whole world is: its sheet + the shared log so far +
its own private log. It replies with a DEPOSIT for the shared log and an
optional NOTE for its private log (parsed leniently). The room stops when
Keeper deposits a FINAL PLAN, or at the turn cap.

Pacing: all model calls are strictly sequential with a >=3.5 s gap,
exponential backoff on HTTP 429, and a hard stop (with state kept) if
429s recur after backoff.

Usage:
    python3 crank.py solo    # control: each agent alone, one shot, no room
    python3 crank.py room    # the experiment: run the room
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROOM = ROOT / "room"
SOLO_DIR = ROOT / "solo"
CHAT_CLI = ROOT.parent / "skills" / "minimax" / "bin" / "chat.py"
RUN_LOG = ROOT / "run-log.json"

AGENTS = ["lookout", "skeptic", "keeper"]
DISPLAY = {"lookout": "Lookout", "skeptic": "Skeptic", "keeper": "Keeper"}
MAX_TURNS = 12
MIN_GAP_S = 3.5  # pacing gate: minimum seconds between model-call starts
MAX_TOKENS = 700

SOLO_TASK = """THE JOB
Produce ONE safe departure plan for tomorrow morning's run: M/V Teal
(28 ft, draft 1.1 m) carries supplies from Greyhook Harbor to Beacon
Island and returns to Greyhook the same morning.

Public facts:
- Two routes run from the bar to Beacon Island: the south channel
  (about 1 h 15 min, bar to island) and the north channel around
  Gull Rock (about 1 h 50 min, bar to island). Same times returning.
- Unloading at Beacon Island takes about 20 minutes.
- Departure is at dawn, and the plan must name concrete clock times."""

_call_count = 0
_last_call_start = 0.0
_events = []
if RUN_LOG.exists():  # keep one continuous call record across processes
    try:
        _events = json.loads(RUN_LOG.read_text())
    except Exception:
        _events = []


def _log_event(**kw):
    _events.append(kw)
    RUN_LOG.write_text(json.dumps(_events, indent=2))


def call_model(prompt, who):
    """One MiniMax-Text-01 call via the fleet skill CLI.

    Pacing gate + 429 backoff. Returns the reply text. Raises SystemExit
    (state kept on disk) if 429s recur after backoff or the call fails
    outright more than twice.
    """
    global _call_count, _last_call_start
    attempt = 0
    while True:
        attempt += 1
        if _call_count:
            wait = MIN_GAP_S - (time.time() - _last_call_start)
            if wait > 0:
                time.sleep(wait)
        _last_call_start = time.time()
        _call_count += 1
        started = time.strftime("%H:%M:%S")
        proc = subprocess.run(
            [sys.executable, str(CHAT_CLI), prompt,
             "--max-tokens", str(MAX_TOKENS)],
            capture_output=True, text=True, timeout=300,
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        is_429 = "429" in (out + "\n" + err)
        ok = bool(out) and proc.returncode == 0
        _log_event(n=_call_count, who=who, started=started, attempt=attempt,
                   ok=ok, rate_limited=is_429)
        if ok:
            if attempt > 1:
                print(f"  [call {_call_count} · {who}] ok on attempt {attempt}")
            return out
        if is_429 and attempt <= 4:
            backoff = 8 * (2 ** (attempt - 1))
            print(f"  [call {_call_count} · {who}] 429 — backoff {backoff}s")
            time.sleep(backoff)
            continue
        if is_429:
            raise SystemExit(
                f"STOP: 429s recur after backoff (call for {who}). "
                "Room state on disk is intact; rerun to continue is NOT "
                "supported in v1 — score what exists.")
        if attempt <= 2:
            print(f"  [call {_call_count} · {who}] error rc={proc.returncode}: "
                  f"{err[:160]} — retrying")
            time.sleep(5)
            continue
        raise SystemExit(f"STOP: model call failed for {who}: {err[:300]}")


def parse_reply(text):
    """Lenient parse of the DEPOSIT:/NOTE: format.

    If the model ignores the format entirely, the whole reply becomes the
    deposit and there is no note — the room keeps turning.
    """
    m = re.search(r"DEPOSIT:\s*(.*?)(?:\n\s*NOTE:|\Z)", text, re.S | re.I)
    deposit = (m.group(1) if m else text).strip()
    n = re.search(r"NOTE:\s*(.*)", text, re.S | re.I)
    note = n.group(1).strip() if n else ""
    if note.lower() in ("none", "n/a", "-", ""):
        note = ""
    return deposit, note


def git_commit(message, author=None):
    subprocess.run(["git", "-C", str(ROOM), "add", "-A"], check=True)
    cmd = ["git", "-C", str(ROOM), "commit", "-q"]
    if author:
        cmd.append(f"--author={author}")
    cmd += ["-m", message]
    subprocess.run(cmd, check=True)


def sheet_of(agent):
    return (ROOM / "agents" / agent / "sheet.md").read_text()


def log_of(agent):
    return (ROOM / "agents" / agent / "log.md").read_text()


def shared_log():
    return (ROOM / "shared.md").read_text()


def run_solo():
    SOLO_DIR.mkdir(exist_ok=True)
    for agent in AGENTS:
        print(f"[solo] {DISPLAY[agent]} alone…")
        prompt = f"""=== YOUR SHEET (who you are, and what you alone know) ===
{sheet_of(agent)}

{SOLO_TASK}

You are working ALONE. There is no room, nobody to ask, nobody to
check your work. Produce the complete departure plan now, in your
own voice, with concrete clock times. Base it only on what you know."""
        reply = call_model(prompt, who=f"solo:{agent}")
        out = SOLO_DIR / f"{agent}.md"
        out.write_text(
            f"# SOLO CONTROL — {DISPLAY[agent]}\n\n"
            f"Same sheet, same task, no room, one shot "
            f"(MiniMax-Text-01 via crank.py solo).\n\n---\n\n{reply}\n")
        print(f"[solo] wrote {out} ({len(reply)} chars)")


def run_room():
    turn = 0
    final_declared = False
    while turn < MAX_TURNS and not final_declared:
        agent = AGENTS[turn % 3]
        round_no = turn // 3 + 1
        name = DISPLAY[agent]
        keeper_extra = ""
        if agent == "keeper":
            keeper_extra = (
                "\nYou are Keeper: if the plan is now complete and safe — "
                "every constraint in this room accounted for — begin your "
                "deposit with \"FINAL PLAN:\" and give the whole plan, "
                "final, with concrete times. If anything is still missing "
                "or unsettled, do NOT declare; name what is missing.\n")
        prompt = f"""You are {name}, an agent in a shared room, and the crank has
given you the floor. This is round {round_no} (turn {turn + 1} of at
most {MAX_TURNS}).

=== YOUR SHEET (who you are, and what you alone know) ===
{sheet_of(agent)}

=== THE SHARED LOG (the room so far — the task, then every deposit) ===
{shared_log()}

=== YOUR PRIVATE LOG (only you see this) ===
{log_of(agent)}

=== YOUR TURN ===
Post ONE deposit to the shared log. Play off the others: answer them,
quote them, challenge them, correct the draft. Do not dump your
private fact every turn — but if the emerging plan conflicts with
something you know, you must speak. Stay in character. Keep the
deposit under ~130 words.{keeper_extra}
Reply in exactly this format:
DEPOSIT: <your message to the room>
NOTE: <one short line for your private log, or: none>"""
        print(f"[room] round {round_no} · {name} thinking…")
        reply = call_model(prompt, who=f"room:{agent}:r{round_no}")
        deposit, note = parse_reply(reply)

        shared_path = ROOM / "shared.md"
        with shared_path.open("a") as f:
            f.write(f"\n### Round {round_no} — {name} (turn {turn + 1})\n\n"
                    f"{deposit}\n")
        if note:
            log_path = ROOM / "agents" / agent / "log.md"
            with log_path.open("a") as f:
                f.write(f"\n## After round {round_no}\n\n{note}\n")
        git_commit(f"R{round_no} · {name} deposits",
                   author=f"{name} <{agent}@room.local>")
        print(f"[room] {name} deposited ({len(deposit)} chars)"
              + (" + private note" if note else ""))
        print("  " + deposit.replace("\n", "\n  ")[:600])
        if agent == "keeper" and deposit.lstrip().upper().startswith("FINAL PLAN"):
            final_declared = True
            print("[room] Keeper declared the FINAL PLAN. Room stops.")
        turn += 1
    print(f"[room] done: {turn} turns, "
          f"final plan declared: {final_declared}, "
          f"total model calls this run: {_call_count}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("solo", "room"):
        print(__doc__)
        raise SystemExit(2)
    if sys.argv[1] == "solo":
        run_solo()
    else:
        run_room()

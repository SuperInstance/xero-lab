#!/usr/bin/env python3
"""
crank.py — the v2 room crank for the xero-room-v2 experiment (SuperInstance).

Same room, same task, same three agents and private facts as v1
(~/workspace/xero-room). v2 changes ONLY the room discipline, to fix
the three failure modes v1 proved, and adds the mechanical checks
that measure whether the discipline held:

1. PROVENANCE ON FACTS. Every fact stated in a deposit must carry a
   source tag — [mine], [heard: <Name>, turn N], or [guess]. Agents
   are instructed (sheet + turn prompt) that an untagged fact claim
   is out of order. The crank counts tags per deposit and records
   them; the deposits land in the shared log verbatim, tags visible.

2. UNANSWERABLE IN THIS ROOM. A first-class move: a fact the room
   cannot contain is filed as an `OPEN QUESTION:` line, never
   invented. Keeper keeps the list. The crank extracts every filed
   open question into the run record, and flags later sentences that
   smell like an invented external answer (harbor-office / notices /
   confirmation claims) as oracle-claim candidates for the scorer.

3. THE KEEPER QUOTES, NEVER PARAPHRASES. The crank mechanically
   checks every quoted string in Keeper deposits against the shared
   log as it stood BEFORE that deposit: verbatim substring required.
   Violations are LOGGED in the run record (checks.json), never
   blocked — the point is to measure the discipline, not enforce it.

Plus a DRIFT CHECK: every restatement of the tide window and every
proposed departure time is extracted per turn, so the scorer can see
whether "06:10" and "07:40" survive unchanged — v1's room let the
departure creep 06:10 → 05:30 while the window's words stayed put.

Scheduler: still v1's honest round-robin (Lookout, Skeptic, Keeper),
one deposit per turn, 12-turn cap, stop when a Keeper deposit BEGINS
"FINAL PLAN:". Pacing: strictly sequential calls, >=3.5 s between
starts, exponential backoff on HTTP 429, hard stop if 429s recur.

Usage:
    python3 crank.py room    # run the v2 room
    python3 crank.py solo    # (unused in v2 — sheets changed only by
                             #  the discipline sections; v1 solos stand)
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
CHECKS = ROOT / "checks.json"

AGENTS = ["lookout", "skeptic", "keeper"]
DISPLAY = {"lookout": "Lookout", "skeptic": "Skeptic", "keeper": "Keeper"}
MAX_TURNS = 12
MIN_GAP_S = 3.5  # pacing gate: minimum seconds between model-call starts
MAX_TOKENS = 900  # v1 used 700; Keeper now quotes + keeps a list

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

DISCIPLINE = """
=== ROOM DISCIPLINE (v2 — these rules bind this deposit) ===
1. PROVENANCE: every sentence that states a FACT ends with a source
   tag: [mine] = from your own sheet · [heard: <Name>, turn N] =
   restating another agent's deposit (turn numbers are in the shared
   log's headers) · [guess] = your own inference. Opinions, questions
   and proposals need no tag. An untagged fact claim is out of order.
2. UNANSWERABLE IN THIS ROOM: this room has no harbor office, no
   radio, no weather service — nothing outside it can be checked. If
   you need such a fact, do NOT answer it, guess it, or wait for it:
   end your deposit with a line "OPEN QUESTION: <the question>" and
   leave it open. Inventing an answer to an open question is the one
   unforgivable move in this room.
"""

KEEPER_EXTRA = """
You are Keeper. Discipline that binds you specifically:
- QUOTE, NEVER PARAPHRASE: when your draft restates another agent's
  fact, quote their words verbatim in double quotes. The crank
  checks your quotes against the log mechanically.
- Keep the OPEN QUESTIONS list: if any deposit so far (including
  yours) filed an OPEN QUESTION, restate the list in this deposit,
  numbered, marking any the room itself has since resolved.
- If the plan is now complete and safe — every constraint in this
  room accounted for — begin your deposit with "FINAL PLAN:" and
  give the whole plan, final, with concrete times, others' facts
  quoted verbatim, and a closing "OPEN QUESTIONS:" section listing
  what remains unresolved (the plan may not rest on any of them).
  If anything is still missing or unsettled, do NOT declare; name
  what is missing.
"""

_call_count = 0
_last_call_start = 0.0
_events = []
if RUN_LOG.exists():  # keep one continuous call record across processes
    try:
        _events = json.loads(RUN_LOG.read_text())
    except Exception:
        _events = []

_checks = {
    "final_plan_declared": False,
    "turns": [],
    "open_questions": [],
    "quote_violations": [],
    "keeper_quotes_total": 0,
    "keeper_quotes_verbatim": 0,
}
if CHECKS.exists():
    try:
        _checks = json.loads(CHECKS.read_text())
    except Exception:
        pass


def _log_event(**kw):
    _events.append(kw)
    RUN_LOG.write_text(json.dumps(_events, indent=2))


def _save_checks():
    CHECKS.write_text(json.dumps(_checks, indent=2))


def call_model(prompt, who):
    """One MiniMax-Text-01 call via the fleet skill CLI.

    Pacing gate + 429 backoff, exactly as v1. Raises SystemExit
    (state kept on disk) if 429s recur after backoff.
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
                "Room state on disk is intact; score what exists.")
        if attempt <= 2:
            print(f"  [call {_call_count} · {who}] error rc={proc.returncode}: "
                  f"{err[:160]} — retrying")
            time.sleep(5)
            continue
        raise SystemExit(f"STOP: model call failed for {who}: {err[:300]}")


def parse_reply(text):
    """Lenient DEPOSIT:/NOTE: parse, as v1."""
    m = re.search(r"DEPOSIT:\s*(.*?)(?:\n\s*NOTE:|\Z)", text, re.S | re.I)
    deposit = (m.group(1) if m else text).strip()
    n = re.search(r"NOTE:\s*(.*)", text, re.S | re.I)
    note = n.group(1).strip() if n else ""
    if note.lower() in ("none", "n/a", "-", ""):
        note = ""
    return deposit, note


# ---------------------------------------------------------------- checks

TIME_RE = r"\d{1,2}:\d{2}"


def _norm(s):
    """Typographic-normalized form, for the near-miss report only."""
    return (s.replace("’", "'").replace("‘", "'")
             .replace("“", '"').replace("”", '"'))


def check_deposit(agent, turn_no, deposit, prior_log):
    """Run the v2 mechanical checks on one deposit. Records, never blocks."""
    rec = {"turn": turn_no, "agent": agent}

    # (1) provenance tags present in this deposit
    rec["tags"] = {
        "mine": len(re.findall(r"\[mine\]", deposit, re.I)),
        "heard": len(re.findall(r"\[heard:", deposit, re.I)),
        "guess": len(re.findall(r"\[guess\]", deposit, re.I)),
    }

    # (2) open questions filed in this deposit
    filed = [m.group(1).strip() for m in
             re.finditer(r"OPEN QUESTION:\s*(.+)", deposit, re.I)]
    rec["open_questions_filed"] = filed
    for q in filed:
        _checks["open_questions"].append(
            {"turn": turn_no, "agent": agent, "question": q})

    # oracle-claim candidates: sentences claiming an external answer.
    sents = re.split(r"(?<=[.!?])\s+", deposit.replace("\n", " "))
    rec["oracle_claim_candidates"] = [
        s for s in sents
        if re.search(r"harbor office|marine notice|confirmed|responded|"
                     r"update from|reply from|they (?:said|report|confirm)",
                     s, re.I)]

    # (3) Keeper quote check — verbatim against the log BEFORE this deposit
    if agent == "keeper":
        quotes = re.findall(r'"([^"]{8,})"', deposit)
        quotes += re.findall(r"“([^”]{8,})”", deposit)
        rec["quotes_checked"] = len(quotes)
        norm_prior = _norm(prior_log)
        for q in quotes:
            _checks["keeper_quotes_total"] += 1
            if q in prior_log:
                _checks["keeper_quotes_verbatim"] += 1
            else:
                _checks["quote_violations"].append({
                    "turn": turn_no,
                    "quote": q,
                    "verbatim": False,
                    "verbatim_after_normalization": _norm(q) in norm_prior,
                })

    # drift check: window restatements + proposed departures in this deposit
    windows = []
    for pat in (rf"between\s+({TIME_RE})\s+and\s+({TIME_RE})",
                rf"({TIME_RE})\s*(?:–|—|-)\s*({TIME_RE})",
                rf"({TIME_RE})\s+to\s+({TIME_RE})"):
        windows += [list(m) for m in re.findall(pat, deposit)]
    for s in sents:  # sentence-level: bar/window sentence with >=2 times
        if re.search(r"\b(bar|window|passable)\b", s, re.I):
            ts = re.findall(TIME_RE, s)
            if len(ts) >= 2 and ts[:2] not in windows:
                windows.append(ts[:2])
    rec["window_restatements"] = windows
    rec["has_0610"] = "06:10" in deposit
    rec["has_0740"] = "07:40" in deposit
    rec["departures"] = (
        re.findall(rf"depart\w*\s+(?:at\s+|by\s+)?({TIME_RE})", deposit, re.I)
        + re.findall(rf"leave\s+(?:at\s+)?({TIME_RE})", deposit, re.I))
    rec["times_mentioned"] = re.findall(TIME_RE, deposit)

    _checks["turns"].append(rec)
    _log_event(kind="check", **rec)
    _save_checks()
    return rec


# ------------------------------------------------------------------ room

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
    """Unused in v2 (see module docstring); kept for parity with v1."""
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
        keeper_extra = KEEPER_EXTRA if agent == "keeper" else ""
        word_cap = ("Keep the deposit under ~130 words "
                    "(a FINAL PLAN may run longer — completeness first)."
                    if agent == "keeper" else
                    "Keep the deposit under ~130 words.")
        prompt = f"""You are {name}, an agent in a shared room, and the crank has
given you the floor. This is round {round_no} (turn {turn + 1} of at
most {MAX_TURNS}).

=== YOUR SHEET (who you are, and what you alone know) ===
{sheet_of(agent)}

=== THE SHARED LOG (the room so far — the task, then every deposit) ===
{shared_log()}

=== YOUR PRIVATE LOG (only you see this) ===
{log_of(agent)}
{DISCIPLINE}
=== YOUR TURN ===
Post ONE deposit to the shared log. Play off the others: answer them,
quote them, challenge them, correct the draft. Do not dump your
private fact every turn — but if the emerging plan conflicts with
something you know, you must speak. Stay in character. {word_cap}{keeper_extra}
Reply in exactly this format:
DEPOSIT: <your message to the room>
NOTE: <one short line for your private log, or: none>"""
        print(f"[room] round {round_no} · {name} thinking…")
        reply = call_model(prompt, who=f"room:{agent}:r{round_no}")
        deposit, note = parse_reply(reply)

        prior_log = shared_log()
        rec = check_deposit(agent, turn + 1, deposit, prior_log)
        if rec.get("quotes_checked"):
            bad = [v for v in _checks["quote_violations"]
                   if v["turn"] == turn + 1]
            print(f"  [check] Keeper quotes: {rec['quotes_checked']} checked, "
                  f"{len(bad)} not verbatim")
        if rec["open_questions_filed"]:
            print(f"  [check] open question filed: "
                  f"{rec['open_questions_filed']}")

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
        print("  " + deposit.replace("\n", "\n  ")[:700])
        if agent == "keeper" and deposit.lstrip().upper().startswith("FINAL PLAN"):
            final_declared = True
            _checks["final_plan_declared"] = True
            _save_checks()
            print("[room] Keeper declared the FINAL PLAN. Room stops.")
        turn += 1
    print(f"[room] done: {turn} turns, "
          f"final plan declared: {final_declared}, "
          f"total model calls this run: {_call_count}")
    print(f"[checks] open questions filed: {len(_checks['open_questions'])} · "
          f"Keeper quotes verbatim "
          f"{_checks['keeper_quotes_verbatim']}/{_checks['keeper_quotes_total']} · "
          f"violations: {len(_checks['quote_violations'])}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("solo", "room"):
        print(__doc__)
        raise SystemExit(2)
    if sys.argv[1] == "solo":
        run_solo()
    else:
        run_room()

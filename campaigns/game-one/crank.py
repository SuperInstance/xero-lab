#!/usr/bin/env python3
"""crank.py — the turn crank for xero-rpg game one.

One MiniMax-Text-01 call per invocation, through the fleet skill
CLI. Pacing gate: strictly sequential (this script is never run in
parallel), >= MIN_GAP seconds between call starts (tracked across
invocations in pacing.jsonl), backoff 30s then 60s on failure, and
a hard stop after the third failure — the game reports, it does
not hammer the provider.

Usage:
  crank.py WHO PURPOSE PROMPT_FILE OUT_FILE [--system FILE] [--max-tokens N]

Every attempt is logged to pacing.jsonl: {t, who, purpose, attempt, ok}.
"""
import json
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
CHAT = os.path.expanduser("~/workspace/skills/minimax/bin/chat.py")
PACE_FILE = os.path.join(BASE, "pacing.jsonl")
MIN_GAP = 3.5
BACKOFFS = [30, 60]  # after attempt 1 and 2; attempt 3 is final


def log_attempt(who, purpose, attempt, ok, note=""):
    entry = {"t": time.time(), "who": who, "purpose": purpose,
             "attempt": attempt, "ok": ok, "note": note}
    with open(PACE_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry["t"]


def last_attempt_time():
    try:
        with open(PACE_FILE) as f:
            lines = [ln for ln in f if ln.strip()]
        return json.loads(lines[-1])["t"] if lines else 0.0
    except FileNotFoundError:
        return 0.0


def wait_for_gap():
    delta = time.time() - last_attempt_time()
    if last_attempt_time() and delta < MIN_GAP:
        time.sleep(MIN_GAP - delta)


def main():
    args = sys.argv[1:]
    who, purpose, prompt_file, out_file = args[0], args[1], args[2], args[3]
    system_text = None
    max_tokens = "4000"
    i = 4
    while i < len(args):
        if args[i] == "--system":
            with open(args[i + 1]) as f:
                system_text = f.read()
            i += 2
        elif args[i] == "--max-tokens":
            max_tokens = args[i + 1]
            i += 2
        else:
            i += 1

    with open(prompt_file) as f:
        prompt = f.read()

    cmd = ["python3", CHAT, prompt, "--max-tokens", max_tokens]
    if system_text:
        cmd += ["--system", system_text]

    for attempt in (1, 2, 3):
        wait_for_gap()
        start = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        err = (proc.stderr or "").strip()
        ok = proc.returncode == 0 and bool(proc.stdout.strip())
        log_attempt(who, purpose, attempt, ok,
                    ("429" if "429" in err else err[:80]) if not ok else "")
        if ok:
            with open(out_file, "w") as f:
                f.write(proc.stdout.strip() + "\n")
            print(f"OK {who}/{purpose} attempt {attempt} "
                  f"({time.time() - start:.1f}s, {len(proc.stdout)} chars)")
            return 0
        print(f"FAIL {who}/{purpose} attempt {attempt}: {err[:160]}",
              file=sys.stderr)
        if attempt <= len(BACKOFFS):
            time.sleep(BACKOFFS[attempt - 1])
    print("HARD STOP: three failed attempts — reporting, not retrying.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""v3 route A — the deterministic pre-reader, alone and with a judge.

Two conditions on 36 FRESH held-out seas (seed 777001, generator v2,
balanced labels — a new seed, disjoint from v1's 4242 and v2's 90210):
  A-alone : prereader.py's estimators answer directly (no model).
  A-judge : MiniMax receives ONLY the instrument brief (no frames)
            and returns the four gist answers + a one-line summary.
            The judge-vs-alone diff isolates the model's added
            value (or damage) per question.
Scored with v1's scorer (reading_test.score), unchanged.

PACING GATE: the v2 runner (sequential, >=3 s gaps, backoff ladder,
abort on a surviving 429) is reused verbatim. Resumable via the
output jsonl.

Usage: python3 route_a_test.py [--limit N] [--analyze]
"""
import argparse, json, os, re, sys, time
from collections import Counter
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reading_test
from tuning_test import build_heldout, call_with_backoff, AbortRun
from prereader import measure, estimator_answer, render_brief

SEED = 777001
OUT = "runs/v3_routeA_results.jsonl"
TRUTHS_OUT = "runs/v3_heldout_truths.json"

SYSTEM = ("You are the judgment layer above a wave instrument. The "
          "instrument has already measured the sea; you never see the "
          "raw stream. Turn the instrument brief into the four gist "
          "answers and one plain line a helmsman can use. Trust the "
          "measurements; where the brief says a value is unknown or "
          "ambiguous, use the remaining measurements and give your "
          "best answer — always answer all four questions.")

USER_TMPL = """{brief}

The four questions concern the DOMINANT wave train:
1. "direction": compass direction the waves are TRAVELLING TOWARD. One of: N NE E SE S SW W NW.
2. "period_s": seconds between crests at a fixed point.
3. "trend": "building", "easing", or "steady".
4. "sets": waves per set/group — an integer, or "none" for a continuous sea.

Answer with exactly one JSON object and nothing else:
{{"direction": "...", "period_s": <number>, "trend": "...", "sets": <integer or "none">, "summary": "<one line: what the helmsman should know>"}}"""


def parse_judge(text):
    ans = reading_test.parse_answer(text)
    summary = None
    if text:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                summary = json.loads(m.group(0)).get("summary")
            except Exception:
                summary = None
    return ans, summary


def load_done(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("kind") == "judge":
                done[r["stream_id"]] = r
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--analyze", action="store_true")
    args = ap.parse_args()
    if args.analyze:
        return analyze()

    streams = build_heldout(36, seed=SEED)
    print(f"held-out: {len(streams)} seas (seed {SEED}, generator v2, balanced)", flush=True)
    with open(TRUTHS_OUT, "w") as f:
        json.dump({str(s["id"]): s["truth"] for s in streams}, f, indent=1)

    # --- A-alone (deterministic, timed) ---
    alone = {}
    t_meas = []
    for s in streams:
        t0 = time.time()
        meas = measure(s["times"], s["frames"], s["sea"])
        t_meas.append(time.time() - t0)
        ans = estimator_answer(meas)
        alone[s["id"]] = {"meas": meas, "answer": ans,
                          "score": reading_test.score(ans, s["truth"])}
        print(f"  [alone] stream {s['id']:2d} meas={meas['direction']}/"
              f"{meas['period_s']}/{meas['trend_class']}/{meas['sets']}", flush=True)
    print(f"estimator cost: {np.mean(t_meas)*1000:.0f} ms/sea (this VM, CPU)", flush=True)

    # --- A-judge (paced MiniMax, brief only) ---
    done = load_done(OUT)
    made = 0
    with open(OUT, "a") as f:
        for s in streams:
            if s["id"] in done:
                continue
            if args.limit and made >= args.limit:
                print("limit reached; stopping (resumable)", flush=True)
                break
            time.sleep(3)
            brief = render_brief(alone[s["id"]]["meas"])
            prompt = USER_TMPL.format(brief=brief)
            t0 = time.time()
            try:
                raw, usage, n429 = call_with_backoff(
                    [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": prompt}])
            except AbortRun as e:
                f.write(json.dumps({"kind": "abort", "stream_id": s["id"],
                                    "reason": str(e)}) + "\n")
                f.flush()
                print(f"ABORT at stream {s['id']}: {e}", flush=True)
                return 2
            dt = time.time() - t0
            ans, summary = parse_judge(raw)
            row = {"kind": "judge", "stream_id": s["id"], "truth": s["truth"],
                   "brief": brief, "meas": alone[s["id"]]["meas"],
                   "alone_answer": alone[s["id"]]["answer"],
                   "alone_score": alone[s["id"]]["score"],
                   "answer": ans, "summary": summary,
                   "score": reading_test.score(ans, s["truth"]),
                   "usage": usage, "latency_s": round(dt, 1), "n429": n429,
                   "prompt_chars": len(prompt)}
            f.write(json.dumps(row) + "\n")
            f.flush()
            made += 1
            print(f"  [judge] stream {s['id']:2d} dir={row['score'].get('direction')} "
                  f"period={row['score'].get('period')} trend={row['score'].get('trend')} "
                  f"sets={row['score'].get('sets')} 429s={n429} {dt:.0f}s", flush=True)
    print("route A run complete", flush=True)
    return analyze()


def _rate(rows, key, sub="score"):
    return sum(1 for r in rows if r[sub].get(key)) / len(rows) if rows else 0.0


def analyze():
    rows = []
    aborts = 0
    for line in open(OUT):
        r = json.loads(line)
        if r.get("kind") == "abort":
            aborts += 1
        elif r.get("kind") == "judge":
            rows.append(r)
    print(f"judge rows={len(rows)} aborts={aborts} total429={sum(r['n429'] for r in rows)}")
    if not rows:
        return 0
    n = len(rows)
    print(f"\n{'question':10s} {'A-alone':>8s} {'A-judge':>8s}")
    for q in ("direction", "direction_within45", "period", "trend", "sets"):
        print(f"{q:10s} {_rate(rows, q, 'alone_score'):8.2f} {_rate(rows, q):8.2f}")
    perrs_a = [r["alone_score"]["period_err_s"] for r in rows
               if r["alone_score"].get("period_err_s") is not None]
    perrs_j = [r["score"]["period_err_s"] for r in rows
               if r["score"].get("period_err_s") is not None]
    print(f"period mean|err|: alone {np.mean(perrs_a):.1f}s (n={len(perrs_a)}), "
          f"judge {np.mean(perrs_j):.1f}s (n={len(perrs_j)})")
    toks = [r["usage"].get("prompt_tokens", 0) for r in rows]
    print(f"judge mean prompt tokens: {np.mean(toks):.0f}")
    # per-question judge effect
    for q in ("direction", "period", "trend", "sets"):
        fixed = sum(1 for r in rows if not r["alone_score"].get(q) and r["score"].get(q))
        broke = sum(1 for r in rows if r["alone_score"].get(q) and not r["score"].get(q))
        print(f"  {q}: judge fixed {fixed}, judge broke {broke}")
    # prior behaviour
    for label, sub in (("alone", "alone_answer"), ("judge", "answer")):
        tc = Counter(r[sub]["trend"] for r in rows if r[sub])
        print(f"  {label} trend answers: {dict(tc)}")
    tt = Counter(r["truth"]["trend"] for r in rows)
    print(f"  truth trends: {dict(tt)}")
    # where the judge overrode a measurement
    for q in ("direction", "trend", "sets"):
        over = [r for r in rows if r["answer"] and r["alone_answer"]
                and r["answer"].get(q if q != "direction" else "direction") != r["alone_answer"].get(q)]
        print(f"  {q}: judge overrode the instrument on {len(over)}/{n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

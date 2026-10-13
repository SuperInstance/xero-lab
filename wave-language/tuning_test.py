#!/usr/bin/env python3
"""v2 tuning run — raise the reader.

v1 verdict: the letter rendering loses nothing to numbers; the
untuned zero-shot reader is the bottleneck. This run applies the
practical tuning lever — few-shot prompting with labeled generator
examples whose work-throughs are MEASURED from the frames (see
authoring.py) — plus a short visible work-through before the answer,
exactly the route RESULTS.md's v2 list prescribes.

Design:
  - Held-out: 36 FRESH seas (seed 90210), generator v2 (randomized
    set-envelope phase), labels exactly balanced: trends 12/12/12,
    sets 9/9/9/9 (3/4/5/none), directions 4-5 each, periods spread.
  - Encoding: letters 20x20 only (the primary condition).
  - Doses (nested example sets): K = 0 (work-through instruction
    only), 1, 2, 4 labeled examples. K=1 runs on 18 streams.
  - PACING GATE: strictly sequential; >=3 s between calls; on HTTP
    429 exponential backoff 30/60/120/240 s; if a call still fails
    after backoff the run ABORTS (writes an abort row) rather than
    losing pairs silently the way v1 did.
  - Resumable: completed (dose, stream) rows in the output file are
    skipped on restart.

Usage: python3 tuning_test.py [--doses 4,0,2,1] [--limit N]
       python3 tuning_test.py --analyze
"""
import argparse, json, os, re, sys, time
import urllib.error
import numpy as np

sys.path.insert(0, "/home/hatch/workspace/skills/minimax/bin")
from chat import chat

sys.path.insert(0, "/home/hatch/workspace/xero-wave-language")
from sea import Sea, sample_stream, COMPASS
from render import assemble_stream
from authoring import build_pool
import reading_test  # for score() — the v1 scorer, unchanged

OUT_DEFAULT = "runs/v2_tuning_results.jsonl"
HELDOUT_SEED = 90210
EXAMPLE_ORDER = [4, 1, 3, 2]   # indices into the seed-777 verified pool
EXAMPLE_FINGERPRINTS = [       # (direction, trend, sets) — drift guard
    ("S", "building", 3), ("NW", "easing", None),
    ("SE", "steady", None), ("NE", "building", 4),
]

SYSTEM = ("You are learning to read a synthetic ocean-wave sensor stream "
          "written in letters. Study the worked examples, then read the "
          "new stream the same way.")

HEADER = """A wave sensor watches a square patch of sea, 300 m across. You are given a time series of snapshots (frames) of wave height over the patch, one frame every 1.25 seconds. In every frame the TOP row is the NORTH edge of the patch and the LEFT column is the WEST edge.

Each frame is a 20x20 grid of letters. A cell's letter is the wave height there: ' ' (space) is the deepest trough, and the letters rise through . : - = + * # % to '@', the highest crest. The height scale is identical in every frame, so a stream whose frames get brighter overall is a sea that is growing.

Frames are grouped by the sea's own rhythm: a line "--- SET ---" marks the start of a group of bigger waves and "~~~ LULL ~~~" marks quieter water between groups (some seas have no clear groups).

Four questions about the DOMINANT (strongest) wave train:
1. "direction": the compass direction the waves are TRAVELLING TOWARD across the patch. One of: N NE E SE S SW W NW.
2. "period_s": the seconds between one crest of the dominant train and the next, measured at a fixed point.
3. "trend": whether the dominant train's height is "building", "easing", or "steady" over the stream.
4. "sets": how many waves are in each set/group — an integer, or "none" if the sea rolls continuously without clear groups.

Work like the examples do, out loud in a few lines: (1) track a bright crest band across frames to see which way the pattern travels; (2) at the centre cell, note the times its brightness peaks and the gaps between peaks — that gap is the period; (3) compare the count of bright cells (letters * and brighter) in the first half of the stream against the second half for the trend; (4) for sets, measure one complete set between LULLs — its length in seconds divided by the period — or, if no complete set fits, use the spacing between SET markers minus the lull; if there is no LULL marker anywhere, the answer is "none".
Then finish with exactly one final line containing only the JSON object: {"direction": "...", "period_s": <number>, "trend": "...", "sets": <integer or "none">}
"""


def build_heldout(n=36, seed=HELDOUT_SEED):
    from collections import Counter
    rng = np.random.default_rng(seed)
    dirs = [COMPASS[i % 8] for i in range(n)]
    periods = [[6.0, 7.0, 8.0, 9.0, 10.0][i % 5] for i in range(n)]
    trends = [["building", "easing", "steady"][i % 3] for i in range(n)]
    setopts = [[3, 4, 5, None][i % 4] for i in range(n)]
    for lst in (dirs, periods, trends, setopts):
        rng.shuffle(lst)
    assert Counter(trends) == {"building": 12, "easing": 12, "steady": 12}, Counter(trends)
    assert Counter(setopts) == {3: 9, 4: 9, 5: 9, None: 9}, Counter(setopts)
    streams = []
    for i in range(n):
        sea = Sea(rng, direction=dirs[i], period_s=periods[i], trend=trends[i], sets=setopts[i])
        times, frames = sample_stream(sea, n=20)
        streams.append({"id": i, "sea": sea, "times": times, "frames": frames,
                        "truth": sea.truth()})
    return streams


def load_examples():
    pool = build_pool(n_candidates=80, seed=777, want=10)
    chosen = []
    for idx, fp in zip(EXAMPLE_ORDER, EXAMPLE_FINGERPRINTS):
        p = pool[idx]
        s = p["sea"]
        got = (s.direction, s.trend, s.sets)
        assert got == fp, f"example pool drift at {idx}: {got} != {fp}"
        body = assemble_stream(p["times"], p["frames"], s.period_s, s.sets,
                               "letters", phase0=s.env_phase0)
        ans = {"direction": s.direction, "period_s": s.period_s,
               "trend": s.trend, "sets": s.sets if s.sets is not None else "none"}
        chosen.append({"stream": body, "workthrough": p["workthrough"],
                       "answer": json.dumps(ans)})
    return chosen


def prompt_for(stream_rec, examples, k):
    parts = [HEADER]
    for j in range(k):
        ex = examples[j]
        parts.append(f"\nEXAMPLE {j + 1}:\nSTREAM:\n{ex['stream']}\n{ex['workthrough']}\nAnswer: {ex['answer']}")
    sea = stream_rec["sea"]
    body = assemble_stream(stream_rec["times"], stream_rec["frames"], sea.period_s,
                           sea.sets, "letters", phase0=sea.env_phase0)
    parts.append(f"\nNOW READ THIS STREAM THE SAME WAY:\nSTREAM:\n{body}\n\n"
                 f"Work through it in a few lines, then finish with the JSON object on its own final line.")
    return "\n".join(parts)


class AbortRun(Exception):
    pass


def call_with_backoff(messages):
    """One call under the pacing gate. Returns (raw_text, usage, n429).
    Raises AbortRun if a 429 survives the full backoff schedule or a
    non-429 error survives its retries."""
    backoff = [30, 60, 120, 240]
    n429 = 0
    other_retries = 0
    while True:
        try:
            data = chat(messages, max_tokens=1500, temperature=0.2)
            br = data.get("base_resp", {}) or {}
            if br.get("status_code", 0) not in (0, None):
                msg = str(br.get("status_msg", ""))
                if "rate" in msg.lower() or br.get("status_code") in (1004, 429):
                    raise urllib.error.HTTPError("api", 429, "Too Many Requests", None, None)
                raise RuntimeError(f"minimax base_resp {br}")
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return raw, data.get("usage", {}), n429
        except urllib.error.HTTPError as e:
            if e.code == 429:
                n429 += 1
                if n429 > len(backoff):
                    raise AbortRun(f"429 persisted through {len(backoff)} backoffs")
                w = backoff[n429 - 1]
                print(f"    [429 #{n429}] backing off {w}s", flush=True)
                time.sleep(w)
            else:
                other_retries += 1
                if other_retries > 2:
                    raise AbortRun(f"HTTP {e.code} persisted")
                time.sleep(10)
        except AbortRun:
            raise
        except Exception as e:
            other_retries += 1
            if other_retries > 2:
                raise AbortRun(f"error persisted: {e}")
            time.sleep(10)


def parse_last_json(text):
    """The answer is the LAST flat JSON object in the response."""
    if not text:
        return None
    cands = re.findall(r"\{[^{}]*\}", text)
    for c in reversed(cands):
        a = reading_test.parse_answer(c)
        if a is not None and a["direction"]:
            return a
    return reading_test.parse_answer(text)


def load_done(path):
    done = set()
    if os.path.exists(path):
        for line in open(path):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("kind") == "result":
                done.add((r["dose"], r["stream_id"]))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doses", default="4,0,2,1")
    ap.add_argument("--streams", type=int, default=36)
    ap.add_argument("--limit", type=int, default=0, help="max NEW calls this invocation")
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--analyze", action="store_true")
    args = ap.parse_args()

    if args.analyze:
        return analyze(args.out)

    examples = load_examples()
    print(f"examples verified: {len(examples)} (nested order {[e['answer'] for e in examples]})", flush=True)
    streams = build_heldout(args.streams)
    print(f"held-out: {len(streams)} seas (seed {HELDOUT_SEED}, generator v2, balanced)", flush=True)

    doses = [int(d) for d in args.doses.split(",")]
    jobs = []
    for d in doses:
        subset = streams if d != 1 else streams[:18]
        jobs += [(d, s) for s in subset]
    done = load_done(args.out)
    todo = [j for j in jobs if (j[0], j[1]["id"]) not in done]
    print(f"jobs: {len(jobs)}, already done: {len(jobs) - len(todo)}, to run: {len(todo)}", flush=True)

    made = 0
    with open(args.out, "a") as f:
        for dose, s in todo:
            if args.limit and made >= args.limit:
                print("limit reached; stopping (resumable)", flush=True)
                break
            time.sleep(3)
            prompt = prompt_for(s, examples, dose)
            t0 = time.time()
            try:
                raw, usage, n429 = call_with_backoff(
                    [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": prompt}])
                err = None
            except AbortRun as e:
                f.write(json.dumps({"kind": "abort", "dose": dose, "stream_id": s["id"],
                                    "reason": str(e)}) + "\n")
                f.flush()
                print(f"ABORT at dose {dose} stream {s['id']}: {e}", flush=True)
                return 2
            dt = time.time() - t0
            ans = parse_last_json(raw)
            row = {"kind": "result", "dose": dose, "stream_id": s["id"],
                   "truth": s["truth"], "answer": ans, "raw": raw[:4000],
                   "score": reading_test.score(ans, s["truth"]), "usage": usage,
                   "latency_s": round(dt, 1), "error": err, "n429": n429,
                   "prompt_chars": len(prompt)}
            f.write(json.dumps(row) + "\n")
            f.flush()
            made += 1
            sc = row["score"]
            print(f"  [dose {dose}] stream {s['id']:2d} parsed={sc.get('parsed')} "
                  f"dir={sc.get('direction')} period={sc.get('period')} "
                  f"trend={sc.get('trend')} sets={sc.get('sets')} "
                  f"429s={n429} {dt:.0f}s", flush=True)
    print("run complete", flush=True)
    return 0


V1_FLOOR = {"direction": 0.21, "direction_within45": 0.50, "period": 0.00,
            "trend": 0.38, "sets": 0.29}


def analyze(path):
    from collections import Counter
    rows = []
    aborts = 0
    for line in open(path):
        r = json.loads(line)
        if r.get("kind") == "abort":
            aborts += 1
        elif r.get("kind") == "result":
            rows.append(r)
    print(f"rows={len(rows)} aborts={aborts} total429={sum(r['n429'] for r in rows)}")
    for dose in sorted({r["dose"] for r in rows}):
        rs = [r for r in rows if r["dose"] == dose]
        n = len(rs)
        def rate(k):
            return sum(1 for r in rs if r["score"].get(k)) / n
        perrs = [r["score"]["period_err_s"] for r in rs if r["score"].get("period_err_s") is not None]
        toks = [r["usage"].get("prompt_tokens", 0) for r in rs]
        tc = Counter(r["answer"]["trend"] for r in rs if r["answer"])
        tt = Counter(r["truth"]["trend"] for r in rs)
        print(f"\ndose K={dose}  n={n} parsed={sum(1 for r in rs if r['score'].get('parsed'))}")
        print(f"  direction {rate('direction'):.2f} (v1 0.21)  within45 {rate('direction_within45'):.2f} (v1 0.50)")
        print(f"  period    {rate('period'):.2f} (v1 0.00)  mean|err| {np.mean(perrs):.1f}s")
        print(f"  trend     {rate('trend'):.2f} (v1 0.38)  answers {dict(tc)} vs truths {dict(tt)}")
        print(f"  sets      {rate('sets'):.2f} (v1 0.29)")
        print(f"  mean prompt tokens {np.mean(toks):.0f}")
        # per-question detail for the headline dose
        dc = Counter((r["truth"]["direction"], r["answer"]["direction"]) for r in rs if r["answer"])
        exact = sum(v for (t, a), v in dc.items() if t == a)
        opp = sum(v for (t, a), v in dc.items()
                  if a in COMPASS and abs(COMPASS.index(t) - COMPASS.index(a)) % 8 in (4,))
        print(f"  direction: exact {exact}, opposite-point {opp}")
        sc_ = Counter(str(r["answer"]["sets"]) for r in rs if r["answer"])
        st = Counter(str(r["truth"]["sets"]) for r in rs)
        print(f"  sets answers {dict(sc_)} vs truths {dict(st)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

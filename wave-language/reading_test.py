#!/usr/bin/env python3
"""Reading test — can a language model read the sea from letters?

Paired design: the SAME synthetic seas are presented to MiniMax under
four encodings:
  letters20 : 20x20 letter grids (the wave language, medium resolution)
  letters12 : 12x12 letter grids (coarse — the adaptive-resolution check)
  numeric   : 20x20 numeric grids, 1-decimal metres (raw-data control)
  summary   : per-frame stats + centre buoy series (instrument control)

Four questions per sea, all with exact ground-truth answers:
direction (8-point), period (s), trend (building/easing/steady),
sets (waves per group, or "none").

Usage (real token counts) is captured from the API response.
Results land in runs/reading_results.jsonl, one row per call.
"""
import argparse, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sea import Sea, sample_stream, COMPASS
from render import assemble_stream, summary_stream

def _load_chat():
    """The reader under test is MiniMax-Text-01, reached through a small
    client module named chat.py exposing
        chat(messages, max_tokens=..., temperature=...) -> API JSON dict
    (the author's fleet skill provides one). Point MINIMAX_CHAT_DIR at
    the folder containing chat.py, or put that folder on PYTHONPATH.
    Returns None when no such module is available."""
    d = os.environ.get("MINIMAX_CHAT_DIR")
    if d:
        sys.path.insert(0, d)
    try:
        from chat import chat
        return chat
    except ImportError:
        return None

chat = _load_chat()

SYSTEM = ("You are reading a synthetic ocean-wave sensor stream. "
          "Answer with a single JSON object only, no other text.")

HEADER = """A wave sensor watches a square patch of sea, 300 m across. You are given a time series of snapshots (frames) of wave height over the patch, one frame every 1.25 seconds. In every frame the TOP row is the NORTH edge of the patch and the LEFT column is the WEST edge.

{encoding}

Frames are grouped by the sea's own rhythm: a line "--- SET ---" marks the start of a group of bigger waves and "~~~ LULL ~~~" marks quieter water between groups (some seas have no clear groups).

Answer four questions about the DOMINANT (strongest) wave train:
1. "direction": the compass direction the waves are TRAVELLING TOWARD across the patch. One of: N NE E SE S SW W NW.
2. "period_s": the seconds between one crest of the dominant train and the next, measured at a fixed point.
3. "trend": whether the dominant train's height is "building", "easing", or "steady" over the stream.
4. "sets": how many waves are in each set/group — an integer, or "none" if the sea rolls continuously without clear groups.

Answer ONLY this JSON object: {{"direction": "...", "period_s": <number>, "trend": "...", "sets": <integer or "none">}}

STREAM:
{stream}
"""

ENC = {
    "letters20": "Each frame is a 20x20 grid of letters. A cell's letter is the wave height there: ' ' (space) is the deepest trough, and the letters rise through . : - = + * # % to '@', the highest crest. The height scale is identical in every frame, so a stream whose frames get brighter overall is a sea that is growing.",
    "letters12": "Each frame is a 12x12 grid of letters. A cell's letter is the wave height there: ' ' (space) is the deepest trough, and the letters rise through . : - = + * # % to '@', the highest crest. The height scale is identical in every frame, so a stream whose frames get brighter overall is a sea that is growing.",
    "numeric": "Each frame is a 20x20 grid of numbers: the wave height in metres at each cell (positive = above mean sea level, negative = below).",
    "summary": "There is no picture. Each line is one frame: the mean, standard deviation, maximum and minimum wave height over the whole patch (metres), and \"buoy\": the height at the centre of the patch at that moment, like a wave buoy's log.",
}

CONDITIONS = ["letters20", "letters12", "numeric", "summary"]


def build_streams(n_streams, seed=4242):
    rng = np.random.default_rng(seed)
    dirs = [COMPASS[i % 8] for i in range(n_streams)]
    trends = [["building", "easing", "steady"][i % 3] for i in range(n_streams)]
    setopts = [[3, 4, 5, None][i % 4] for i in range(n_streams)]
    rng.shuffle(dirs); rng.shuffle(trends); rng.shuffle(setopts)
    streams = []
    for i in range(n_streams):
        sea = Sea(rng, direction=dirs[i], trend=trends[i], sets=setopts[i])
        times, frames20 = sample_stream(sea, n=20)
        _, frames12 = sample_stream(sea, n=12)
        streams.append({
            "id": i, "sea": sea, "times": times,
            "frames20": frames20, "frames12": frames12,
            "truth": sea.truth(),
        })
    return streams


def prompt_for(cond, s):
    sea = s["sea"]
    if cond == "letters20":
        body = assemble_stream(s["times"], s["frames20"], sea.period_s, sea.sets, "letters")
    elif cond == "letters12":
        body = assemble_stream(s["times"], s["frames12"], sea.period_s, sea.sets, "letters")
    elif cond == "numeric":
        body = assemble_stream(s["times"], s["frames20"], sea.period_s, sea.sets, "numeric")
    else:
        body = summary_stream(s["times"], s["frames20"], sea.period_s, sea.sets)
    return HEADER.format(encoding=ENC[cond], stream=body)


def parse_answer(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except Exception:
        return None
    out = {}
    out["direction"] = str(d.get("direction", "")).strip().upper()
    try:
        out["period_s"] = float(d.get("period_s"))
    except Exception:
        out["period_s"] = None
    out["trend"] = str(d.get("trend", "")).strip().lower()
    sv = d.get("sets")
    if isinstance(sv, str) and sv.strip().lower() in ("none", "no", "continuous"):
        out["sets"] = "none"
    else:
        try:
            out["sets"] = int(float(sv))
        except Exception:
            out["sets"] = None
    return out


def compass_dist(a, b):
    if a not in COMPASS or b not in COMPASS:
        return None
    d = abs(COMPASS.index(a) - COMPASS.index(b)) % 8
    return min(d, 8 - d)


def score(ans, truth):
    if ans is None:
        return {"parsed": False}
    sc = {"parsed": True}
    sc["direction"] = ans["direction"] == truth["direction"]
    cd = compass_dist(ans["direction"], truth["direction"])
    sc["direction_within45"] = (cd is not None and cd <= 1)
    if ans["period_s"] is not None:
        err = abs(ans["period_s"] - truth["period_s"])
        sc["period_err_s"] = round(err, 2)
        sc["period"] = err <= max(1.0, 0.15 * truth["period_s"])
    else:
        sc["period_err_s"] = None
        sc["period"] = False
    sc["trend"] = ans["trend"] == truth["trend"]
    sc["sets"] = ans["sets"] == truth["sets"]
    return sc


def run_call(job):
    cond, s = job
    prompt = prompt_for(cond, s)
    t0 = time.time()
    err = None
    raw, usage = "", {}
    for attempt in range(3):
        try:
            data = chat([{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": prompt}],
                        max_tokens=1000, temperature=0.2)
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            err = None
            break
        except Exception as e:
            err = str(e)
            time.sleep(2 * (attempt + 1))
    dt = time.time() - t0
    ans = parse_answer(raw) if raw else None
    return {
        "stream_id": s["id"], "condition": cond, "truth": s["truth"],
        "answer": ans, "raw": raw[:2000], "score": score(ans, s["truth"]),
        "usage": usage, "latency_s": round(dt, 1), "error": err,
        "prompt_chars": len(prompt),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--streams", type=int, default=36)
    ap.add_argument("--conditions", default=",".join(CONDITIONS))
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default="runs/reading_results.jsonl")
    args = ap.parse_args()

    if chat is None:
        sys.exit("reading_test.py: no MiniMax `chat` module found — the "
                 "reading test sends every sea to MiniMax-Text-01 through "
                 "a small client module (chat.py) exposing chat(messages, "
                 "max_tokens=..., temperature=...) -> API JSON.\n"
                 "Supply one with:\n"
                 "  MINIMAX_CHAT_DIR=/path/to/folder-with-chat.py "
                 "python3 reading_test.py --streams 36\n"
                 "  (or put that folder on PYTHONPATH.)\n"
                 "The rest of this folder (sea.py, make_samples.py, "
                 "daylog.py) runs offline with no credentials.")

    conds = args.conditions.split(",")
    streams = build_streams(args.streams)
    jobs = [(c, s) for s in streams for c in conds]
    print(f"{len(jobs)} calls ({args.streams} streams x {len(conds)} conditions)", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, r in enumerate(ex.map(run_call, jobs)):
            results.append(r)
            print(f"  [{i+1}/{len(jobs)}] stream {r['stream_id']} {r['condition']} "
                  f"err={r['error']} usage={r['usage'].get('total_tokens')}", flush=True)
    with open(args.out, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    # summary
    print("\n=== SUMMARY ===")
    for cond in conds:
        rows = [r for r in results if r["condition"] == cond]
        ok = [r for r in rows if r["score"].get("parsed")]
        n = len(rows)
        def rate(key):
            return sum(1 for r in rows if r["score"].get(key)) / n if n else 0
        toks = [r["usage"].get("prompt_tokens", 0) for r in rows]
        perrs = [r["score"]["period_err_s"] for r in rows if r["score"].get("period_err_s") is not None]
        print(f"{cond:10s} n={n} parsed={len(ok)} dir={rate('direction'):.2f} "
              f"dir45={rate('direction_within45'):.2f} period={rate('period'):.2f} "
              f"(mean err {np.mean(perrs):.1f}s) trend={rate('trend'):.2f} sets={rate('sets'):.2f} "
              f"mean_prompt_tokens={np.mean(toks):.0f}")


if __name__ == "__main__":
    main()

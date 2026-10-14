#!/usr/bin/env python3
"""v4 evaluation — envelope-aware trend + truncated-window sets.

Fresh held-out set: 36 seas, seed 1000003 (disjoint from v1's 4242,
v2's 90210, v3's 777001, the student pool's 555000 and the example
pool's 777), generator v2, balanced labels, built by the same
build_heldout construction as v2/v3. Both instruments — v3
(prereader.measure) and v4 (prereader_v4.measure_v4) — run on the
SAME seas, scored with v1's scorer (reading_test.score) unchanged,
so the comparison is exactly paired. Direction/period under v4
double as the regression check: v4 imports the identical estimators.

No model calls. Usage: python3 route_a_v4_test.py
"""
import json, os, sys, time
from collections import Counter
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reading_test
from tuning_test import build_heldout
from prereader import measure, estimator_answer
from prereader_v4 import measure_v4, estimator_answer_v4

SEED = 1000003
OUT = "runs/v4_results.jsonl"
TRUTHS_OUT = "runs/v4_heldout_truths.json"
TRENDS = ["building", "easing", "steady"]


def main():
    streams = build_heldout(36, seed=SEED)
    print(f"held-out: {len(streams)} seas (seed {SEED}, generator v2, balanced)", flush=True)
    with open(TRUTHS_OUT, "w") as f:
        json.dump({str(s["id"]): s["truth"] for s in streams}, f, indent=1)

    rows = []
    t3 = t4 = 0.0
    with open(OUT, "w") as f:
        for s in streams:
            t0 = time.time(); m3 = measure(s["times"], s["frames"], s["sea"]); t3 += time.time() - t0
            t0 = time.time(); m4 = measure_v4(s["times"], s["frames"], s["sea"]); t4 += time.time() - t0
            a3, a4 = estimator_answer(m3), estimator_answer_v4(m4)
            row = {"stream_id": s["id"], "truth": s["truth"],
                   "v3_meas": m3, "v3_answer": a3, "v3_score": reading_test.score(a3, s["truth"]),
                   "v4_meas": m4, "v4_answer": a4, "v4_score": reading_test.score(a4, s["truth"])}
            rows.append(row)
            f.write(json.dumps(row) + "\n"); f.flush()
            print(f"  stream {s['id']:2d} truth={s['truth']['trend']:8s}/{s['truth']['sets']}  "
                  f"v3 trend={a3['trend']} sets={a3['sets']}  "
                  f"v4 trend={a4['trend']}({m4['trend_diag'].get('method')}) "
                  f"sets={a4['sets']}({m4['sets_info'].get('method')})", flush=True)
    n = len(rows)
    print(f"\nestimator cost: v3 {t3/n*1000:.0f} ms/sea, v4 {t4/n*1000:.0f} ms/sea (this VM, CPU)")

    def rate(rows, ver, q):
        return sum(1 for r in rows if r[f"{ver}_score"].get(q)) / n

    print(f"\n{'question':18s} {'v3':>6s} {'v4':>6s}   (same 36 seas, seed {SEED})")
    for q in ("direction", "direction_within45", "period", "trend", "sets"):
        print(f"{q:18s} {rate(rows, 'v3', q):6.2f} {rate(rows, 'v4', q):6.2f}")
    for ver in ("v3", "v4"):
        errs = [r[f"{ver}_score"]["period_err_s"] for r in rows
                if r[f"{ver}_score"].get("period_err_s") is not None]
        print(f"period mean|err| {ver}: {np.mean(errs):.2f}s (n={len(errs)})")

    # trend confusion (truth x answer), ordinal class order
    ORD = ["building", "steady", "easing"]
    for ver in ("v3", "v4"):
        conf = Counter((r["truth"]["trend"], r[f"{ver}_answer"]["trend"]) for r in rows)
        print(f"\n{ver} trend confusion (rows=truth, cols=answer):")
        print(f"{'':10s}" + "".join(f"{c:>10s}" for c in ORD + ["ambiguous"]))
        for t in ORD:
            print(f"{t:10s}" + "".join(f"{conf.get((t, c), 0):10d}" for c in ORD + ["ambiguous"]))
        one_step = sum(v for (t, a), v in conf.items()
                       if a in ORD and abs(ORD.index(t) - ORD.index(a)) == 1)
        two_step = sum(v for (t, a), v in conf.items()
                       if a in ORD and abs(ORD.index(t) - ORD.index(a)) == 2)
        print(f"  one-step errors (to the adjacent slope class): {one_step}, "
              f"two-step (building<->easing): {two_step}")

    # sets: callable/unknown split + methods
    for ver, key in (("v3", "v3_answer"), ("v4", "v4_answer")):
        unk = [r for r in rows if r[key]["sets"] is None]
        called = [r for r in rows if r[key]["sets"] is not None]
        right = sum(1 for r in called if r[f"{ver}_score"].get("sets"))
        print(f"\n{ver} sets: callable {len(called)}/36 ({right} right), unknown {len(unk)}")
    meth = Counter(r["v4_meas"]["sets_info"].get("method") for r in rows)
    print(f"v4 sets methods: {dict(meth)}")
    unk4 = [r["stream_id"] for r in rows if r["v4_answer"]["sets"] is None]
    print(f"v4 sets unknown stream ids: {unk4}")
    amb = [r["stream_id"] for r in rows if r["v4_answer"]["trend"] == "ambiguous"]
    print(f"v4 trend ambiguous stream ids: {amb}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

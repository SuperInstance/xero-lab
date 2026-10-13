#!/usr/bin/env python3
"""v3 route B, diagnostic variant B2 — is the bind the representation?

Route B's flattened-letters MLP sat at chance even on its own
training seas (underfit, flat dose curve). B2 changes ONE thing: the
input gains a motion channel — pooled frame-to-frame letter
differences alongside the pooled letters — so phase motion is
explicit in the input instead of something the MLP must synthesize
from 4,500 static numbers. Still a small numpy MLP reading letters;
no hand-computed statistics (no FFT, no peak counts — raw diffs).

Same pool seed (555000 -> the identical training seas), same held-out
(seed 777001), doses 2048 / 8192, epochs 30 (3x route B's, to give
optimization room). Labeled a diagnostic variant, not a replacement:
route B's headline numbers stand as run.
"""
import json, sys, time
from collections import Counter
import numpy as np

sys.path.insert(0, "/home/hatch/workspace/xero-wave-language")
import reading_test
from sea import Sea, sample_stream, COMPASS
from render import letter_index
from tuning_test import build_heldout
from student import Student, labels, answer_of, POOL_SEED, HELDOUT_SEED


def features_motion(frames):
    idx = letter_index(frames).astype(np.float32)
    T = idx.shape[0]
    pooled = idx.reshape(T, 10, 2, 10, 2).mean(axis=(2, 4)) / 9.0
    diffs = np.diff(idx, axis=0)
    dpooled = diffs.reshape(T - 1, 10, 2, 10, 2).mean(axis=(2, 4)) / 9.0
    return np.concatenate([pooled.reshape(-1), dpooled.reshape(-1)]).astype(np.float32)


def main():
    doses = [2048, 8192]
    epochs = 30
    streams = build_heldout(36, seed=HELDOUT_SEED)
    Xh = np.stack([features_motion(s["frames"]) for s in streams])

    rng = np.random.default_rng(POOL_SEED)
    n = max(doses)
    X = np.empty((n, Xh.shape[1]), dtype=np.float32)
    Y = np.empty((n, 4), dtype=np.int64)
    t0 = time.time()
    for i in range(n):
        sea = Sea(rng)
        _, frames = sample_stream(sea, n=20)
        X[i] = features_motion(frames)
        Y[i] = labels(sea)
    print(f"pool {n} seas with motion features ({time.time()-t0:.0f}s), dim={X.shape[1]}", flush=True)

    out = {"variant": "B2-motion-channels", "epochs": epochs, "doses": {}}
    for dose in doses:
        print(f"\n=== B2 dose {dose} ===", flush=True)
        st = Student(np.random.default_rng(1234), d_in=X.shape[1])
        if dose == doses[0]:
            print(f"student parameters: {st.count():,}", flush=True)
            out["params"] = st.count()
        t0 = time.time()
        st.train(X[:dose], Y[:dose], epochs=epochs)
        train_s = time.time() - t0
        t0 = time.time()
        P = st.predict(Xh)
        infer_ms = (time.time() - t0) / len(Xh) * 1000
        rows = []
        for s, prow in zip(streams, P):
            ans = answer_of(prow)
            rows.append({"stream_id": s["id"], "truth": s["truth"], "answer": ans,
                         "score": reading_test.score(ans, s["truth"])})
        acc = {q: sum(1 for r in rows if r["score"].get(q)) / len(rows)
               for q in ("direction", "direction_within45", "period", "trend", "sets")}
        perrs = [r["score"]["period_err_s"] for r in rows
                 if r["score"].get("period_err_s") is not None]
        out["doses"][str(dose)] = {
            "accuracy": acc, "period_mean_err_s": float(np.mean(perrs)),
            "train_wall_s": round(train_s, 1), "infer_ms_per_sea": round(infer_ms, 2),
            "trend_answers": dict(Counter(r["answer"]["trend"] for r in rows)),
            "rows": rows}
        print(f"  held-out: dir={acc['direction']:.2f} dir45={acc['direction_within45']:.2f} "
              f"period={acc['period']:.2f} (err {np.mean(perrs):.1f}s) trend={acc['trend']:.2f} "
              f"sets={acc['sets']:.2f} | train {train_s:.0f}s", flush=True)
    with open("runs/v3_routeB2_results.json", "w") as f:
        json.dump(out, f, indent=1)
    print("\nwrote runs/v3_routeB2_results.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

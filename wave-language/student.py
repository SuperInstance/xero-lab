#!/usr/bin/env python3
"""v3 route B — the trained small reader (the jev-student pattern).

A genuinely small model, trained LOCALLY on generator output, reads
letter frames directly. No torch/sklearn on this VM, so the student
is a numpy MLP with hand-rolled backprop + Adam:

  input : 45 frames x 20x20 letter indices, 2x2 average-pooled to
          10x10 per frame, scaled to [0,1]  -> 4500 floats
  hidden: 4500 -> 96 -> 64 (ReLU)
  heads : direction (8), period (5: 6/7/8/9/10 s), trend (3),
          sets (4: 3/4/5/none) — softmax each, summed cross-entropy
  size  : ~0.44M parameters (counted exactly at runtime) — the class
          of model a Jetson runs without noticing.

Dose curve: nested training sets of 512 / 2048 / 8192 generator seas
(one pool, first-N), same hyperparameters and epochs at every dose,
graded on the SAME v3 held-out seas as route A (seed 777001).
Training seeds are disjoint from every test seed (4242, 90210,
777001). No API calls at all on this route.

Usage: python3 student.py [--doses 512,2048,8192] [--epochs 10]
"""
import argparse, json, sys, time
from collections import Counter
import numpy as np

sys.path.insert(0, "/home/hatch/workspace/xero-wave-language")
import reading_test
from sea import Sea, sample_stream, COMPASS
from render import letter_index
from tuning_test import build_heldout

PERIODS = [6.0, 7.0, 8.0, 9.0, 10.0]
TRENDS = ["building", "easing", "steady"]
SETOPTS = [3, 4, 5, "none"]
POOL_SEED = 555000
HELDOUT_SEED = 777001


def features(frames):
    """(45,20,20) heights -> (4500,) float32 pooled letter vector."""
    idx = letter_index(frames).astype(np.float32) / 9.0
    T = idx.shape[0]
    pooled = idx.reshape(T, 10, 2, 10, 2).mean(axis=(2, 4))
    return pooled.reshape(-1).astype(np.float32)


def labels(sea):
    tr = sea.truth()
    return (COMPASS.index(tr["direction"]), PERIODS.index(tr["period_s"]),
            TRENDS.index(tr["trend"]), SETOPTS.index(tr["sets"]))


def gen_pool(n, seed=POOL_SEED):
    rng = np.random.default_rng(seed)
    X = np.empty((n, 4500), dtype=np.float32)
    Y = np.empty((n, 4), dtype=np.int64)
    t0 = time.time()
    for i in range(n):
        sea = Sea(rng)
        _, frames = sample_stream(sea, n=20)
        X[i] = features(frames)
        Y[i] = labels(sea)
        if (i + 1) % 2048 == 0:
            print(f"  pool {i+1}/{n} ({time.time()-t0:.0f}s)", flush=True)
    return X, Y


class Student:
    def __init__(self, rng, d_in=4500, h1=96, h2=64):
        def he(fan_in, shape):
            return rng.normal(0, np.sqrt(2.0 / fan_in), size=shape).astype(np.float32)
        self.W1 = he(d_in, (d_in, h1)); self.b1 = np.zeros(h1, np.float32)
        self.W2 = he(h1, (h1, h2));     self.b2 = np.zeros(h2, np.float32)
        self.heads = [(he(h2, (h2, k)), np.zeros(k, np.float32))
                      for k in (8, 5, 3, 4)]
        self.params = [self.W1, self.b1, self.W2, self.b2]
        for W, b in self.heads:
            self.params += [W, b]

    def count(self):
        return int(sum(p.size for p in self.params))

    def forward(self, X):
        Z1 = X @ self.W1 + self.b1
        A1 = np.maximum(Z1, 0)
        Z2 = A1 @ self.W2 + self.b2
        A2 = np.maximum(Z2, 0)
        logits = [A2 @ W + b for W, b in self.heads]
        return Z1, A1, Z2, A2, logits

    @staticmethod
    def _softmax(z):
        z = z - z.max(axis=1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(axis=1, keepdims=True)

    def train(self, X, Y, epochs=10, batch=128, lr=2e-3, wd=1e-4, seed=99):
        rng = np.random.default_rng(seed)
        ms = [np.zeros_like(p) for p in self.params]
        vs = [np.zeros_like(p) for p in self.params]
        step = 0
        n = len(X)
        for ep in range(epochs):
            perm = rng.permutation(n)
            for i in range(0, n, batch):
                idx = perm[i:i + batch]
                xb, yb = X[idx], Y[idx]
                B = len(idx)
                Z1, A1, Z2, A2, logits = self.forward(xb)
                grads = [np.zeros_like(p) for p in self.params]
                dA2 = np.zeros_like(A2)
                for h, (W, b) in enumerate(self.heads):
                    p = self._softmax(logits[h])
                    p[np.arange(B), yb[:, h]] -= 1.0
                    dlog = p / (B * 4.0)          # 4 heads averaged
                    grads[4 + 2 * h] = A2.T @ dlog + wd * W
                    grads[4 + 2 * h + 1] = dlog.sum(axis=0)
                    dA2 += dlog @ W.T
                dZ2 = dA2 * (Z2 > 0)
                grads[2] = A1.T @ dZ2 + wd * self.W2
                grads[3] = dZ2.sum(axis=0)
                dA1 = dZ2 @ self.W2.T
                dZ1 = dA1 * (Z1 > 0)
                grads[0] = xb.T @ dZ1 + wd * self.W1
                grads[1] = dZ1.sum(axis=0)
                step += 1
                for j, par in enumerate(self.params):
                    ms[j] = 0.9 * ms[j] + 0.1 * grads[j]
                    vs[j] = 0.999 * vs[j] + 0.001 * grads[j] ** 2
                    mh = ms[j] / (1 - 0.9 ** step)
                    vh = vs[j] / (1 - 0.999 ** step)
                    par -= lr * mh / (np.sqrt(vh) + 1e-8)
            if ep == epochs - 1:
                acc = self.accuracy(X[:512], Y[:512])
                print(f"    epoch {ep+1}/{epochs} train-head-acc (first512) "
                      f"dir={acc[0]:.2f} per={acc[1]:.2f} trend={acc[2]:.2f} sets={acc[3]:.2f}",
                      flush=True)

    def predict(self, X):
        _, _, _, _, logits = self.forward(X)
        return np.stack([lg.argmax(axis=1) for lg in logits], axis=1)

    def accuracy(self, X, Y):
        P = self.predict(X)
        return tuple(float((P[:, h] == Y[:, h]).mean()) for h in range(4))


def answer_of(pred_row):
    d, p, t, s = (int(v) for v in pred_row)
    return {"direction": COMPASS[d], "period_s": PERIODS[p],
            "trend": TRENDS[t], "sets": SETOPTS[s]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doses", default="512,2048,8192")
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--out", default="runs/v3_routeB_results.json")
    args = ap.parse_args()
    doses = [int(d) for d in args.doses.split(",")]

    # held-out — identical construction to route A; cross-check truths
    streams = build_heldout(36, seed=HELDOUT_SEED)
    try:
        saved = json.load(open("runs/v3_heldout_truths.json"))
        assert all(saved[str(s["id"])] == s["truth"] for s in streams), "truth mismatch"
        print("held-out truths cross-checked against route A file: identical", flush=True)
    except FileNotFoundError:
        print("route A truths file not present; using local rebuild", flush=True)
    Xh = np.stack([features(s["frames"]) for s in streams])
    Yh = np.array([labels(s["sea"]) for s in streams])

    pool_n = max(doses)
    print(f"generating pool of {pool_n} training seas (seed {POOL_SEED})...", flush=True)
    X, Y = gen_pool(pool_n)
    dist = {h: dict(Counter(Y[:, i].tolist())) for i, h in
            enumerate(("dir", "period", "trend", "sets"))}
    print(f"pool label distribution: {dist}", flush=True)

    results = {"heldout_seed": HELDOUT_SEED, "pool_seed": POOL_SEED,
               "feature_dim": int(X.shape[1]), "doses": {}}
    for dose in doses:
        print(f"\n=== dose {dose} seas ===", flush=True)
        rng = np.random.default_rng(1234)
        st = Student(rng)
        if dose == doses[0]:
            print(f"student parameters: {st.count():,}", flush=True)
            results["params"] = st.count()
        t0 = time.time()
        st.train(X[:dose], Y[:dose], epochs=args.epochs)
        train_s = time.time() - t0
        # inference timing (single-sea forwards)
        t0 = time.time()
        P = st.predict(Xh)
        infer_ms = (time.time() - t0) / len(Xh) * 1000
        rows = []
        for s, prow in zip(streams, P):
            ans = answer_of(prow)
            rows.append({"stream_id": s["id"], "truth": s["truth"],
                         "answer": ans, "score": reading_test.score(ans, s["truth"])})
        acc = {q: sum(1 for r in rows if r["score"].get(q)) / len(rows)
               for q in ("direction", "direction_within45", "period", "trend", "sets")}
        perrs = [r["score"]["period_err_s"] for r in rows
                 if r["score"].get("period_err_s") is not None]
        trend_answers = dict(Counter(r["answer"]["trend"] for r in rows))
        results["doses"][str(dose)] = {
            "accuracy": acc, "period_mean_err_s": float(np.mean(perrs)),
            "train_wall_s": round(train_s, 1), "infer_ms_per_sea": round(infer_ms, 2),
            "trend_answers": trend_answers, "rows": rows}
        print(f"  held-out: dir={acc['direction']:.2f} dir45={acc['direction_within45']:.2f} "
              f"period={acc['period']:.2f} (err {np.mean(perrs):.1f}s) "
              f"trend={acc['trend']:.2f} sets={acc['sets']:.2f} | "
              f"train {train_s:.0f}s, infer {infer_ms:.1f} ms/sea", flush=True)
        print(f"  trend answers: {trend_answers}", flush=True)

    with open(args.out, "w") as f:
        json.dump(results, f, indent=1)
    print(f"\nwrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

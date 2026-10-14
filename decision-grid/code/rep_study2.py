#!/usr/bin/env python3
"""REP study, phase 2: feature table + candidate REP rules, split-half.

Features use ONLY fields in data/sample.jsonl (name, d, l, fork,
gold_family) with family statistics computed inside the sample.
No stratum feature (sampling artifact = leakage). Read-only vs data/.
"""
import json, re, sys, math
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from standards import disp_rule, pillar_silver, ANCHORS

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data"
sample = {json.loads(l)["name"]: json.loads(l) for l in open(D / "sample.jsonl")}
big = {json.loads(l)["name"]: json.loads(l) for l in open(D / "big_labels.jsonl")}

WORD = re.compile(r"[a-z0-9]+")
def words(t): return set(WORD.findall((t or "").lower()))
def toks(n): return re.split(r"[-_.]", n.lower())

# corpus IDF over the 395 descriptions
df = Counter()
for r in sample.values():
    for w in words(r.get("d")): df[w] += 1
N = len(sample)
def idf(w): return math.log((N + 1) / (df[w] + 1)) + 1.0

# leave-self-out family centroid: words used by >=2 OTHER members of the family
fam_members = defaultdict(list)
for name, r in sample.items(): fam_members[r["gold_family"]].append(name)
def centroid_loo(name):
    fam = sample[name]["gold_family"]
    if fam == "OTHER": return None
    c = Counter()
    for m in fam_members[fam]:
        if m != name:
            for w in words(sample[m].get("d")): c[w] += 1
    return {w for w, k in c.items() if k >= 2}

# family pillar prevalence (SILVER tags over the 395 sample) — context stat
fam_silver = {n: pillar_silver(n, sample[n].get("d")) for n in sample}
def pillar_prev(fam, pillar):
    ms = fam_members[fam]
    if not ms: return 0.0
    return sum(1 for m in ms if pillar in fam_silver[m]) / len(ms)

def feats(name):
    r = sample[name]; fam = r["gold_family"]; dw = words(r.get("d")); t = toks(name)
    cen = centroid_loo(name)
    ovl = (len(dw & cen) / len(dw)) if (cen is not None and dw) else None
    f = {
        "fam": fam, "fork": r["fork"], "anchor": name.lower() in ANCHORS,
        "bare": fam != "OTHER" and name.lower() == fam,
        "fused": fam != "OTHER" and t[0] != fam and name.lower().startswith(fam),
        "descw": len(dw), "ovl": ovl,
        "mean_idf": round(sum(idf(w) for w in dw) / len(dw), 2) if dw else None,
        "nodesc": not (r.get("d") or "").strip(),
    }
    b = big.get(name)
    if b and b["PILLAR"] and fam != "OTHER":
        f["pil_prev"] = round(max(pillar_prev(fam, p) for p in b["PILLAR"]), 2)
    return f

def base_pred(name):
    b = big[name]
    return disp_rule(b["FAM"], b["PILLAR"], name, sample[name]["fork"])

def acc(pred_fn, names):
    ok = sum(1 for n in names if pred_fn(n) == big[n]["DISP"])
    return ok, len(names), ok / len(names)

ALL = sorted(big)
print("feature table for the two contested boundaries")
print("A) pred=DEEP & FAM!=OTHER (REF: DEEP=keep, COLLAPSE=downgrade target)")
for n in ALL:
    if base_pred(n) == "DEEP" and big[n]["FAM"] != "OTHER":
        f = feats(n)
        print(f"  {n:28s} ref={big[n]['DISP']:8s} ovl={f['ovl']} pil_prev={f.get('pil_prev')} descw={f['descw']:3d} idf={f['mean_idf']} anchor={f['anchor']} bare={f['bare']}")
print("B) pred=DEEP & FAM==OTHER (REF: DEEP=keep, TAIL=downgrade target)")
for n in ALL:
    if base_pred(n) == "DEEP" and big[n]["FAM"] == "OTHER":
        f = feats(n)
        print(f"  {n:28s} ref={big[n]['DISP']:8s} descw={f['descw']:3d} idf={f['mean_idf']} fork={f['fork']} anchor={f['anchor']} desc={sample[n].get('d')!r}")
print("C) pred=COLLAPSE (REF: COLLAPSE=keep, TAIL=downgrade target)")
for n in ALL:
    if base_pred(n) == "COLLAPSE":
        f = feats(n)
        mark = " <== REF TAIL" if big[n]["DISP"] == "TAIL" else ""
        print(f"  {n:28s} ref={big[n]['DISP']:8s} descw={f['descw']:3d} idf={f['mean_idf']} nodesc={f['nodesc']} ovl={f['ovl']}{mark}")

# ---------- candidate variants ----------
def v1(theta):
    def f(name):
        p = base_pred(name); b = big[name]; ft = feats(name)
        if p == "DEEP" and b["FAM"] != "OTHER" and not ft["anchor"] and ft["ovl"] is not None and ft["ovl"] >= theta:
            return "COLLAPSE"
        return p
    return f
def v2(name):  # stray-fork gate
    p = base_pred(name); b = big[name]; ft = feats(name)
    if p == "DEEP" and ft["fork"] and b["FAM"] == "OTHER" and not ft["anchor"]:
        return "TAIL"
    return p
def v3(phi):
    def f(name):
        p = base_pred(name); b = big[name]; ft = feats(name)
        if p == "DEEP" and b["FAM"] != "OTHER" and not ft["anchor"] and ft.get("pil_prev") is not None and ft["pil_prev"] >= phi:
            return "COLLAPSE"
        return p
    return f

print("\n--- full-set (in-sample) variant scores vs REF, n=119 ---")
print("BASE            :", acc(base_pred, ALL))
for th in (0.25, 0.28, 0.30, 0.35, 0.40):
    print(f"V1 ovl>={th:<5}    :", acc(v1(th), ALL))
print("V2 fork-gate    :", acc(v2, ALL))
for ph in (0.15, 0.20, 0.25, 0.30):
    print(f"V3 pilprev>={ph:<4} :", acc(v3(ph), ALL))

print("\n--- split-half (tune on one half, test on the other; halves = even/odd by sorted name) ---")
A, B = ALL[::2], ALL[1::2]
for label, tune, test in (("tune A -> test B", A, B), ("tune B -> test A", B, A)):
    print(label, "| base on test half:", acc(base_pred, test))
    for fam_name, mk, grid in (("V1", v1, (0.25, 0.28, 0.30, 0.35, 0.40)), ("V3", v3, (0.15, 0.20, 0.25, 0.30))):
        best = max(grid, key=lambda g: acc(mk(g), tune)[2])
        print(f"   {fam_name}: best-on-tune theta={best} tune={acc(mk(best), tune)} test={acc(mk(best), test)}")

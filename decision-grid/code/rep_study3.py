#!/usr/bin/env python3
"""REP study, phase 3: flip accounting, combined variant + split-half,
production-chain check, and REP values for all 395 repos.

REP (family-typicality): for a repo in family F with pillar tags P,
REP-typicality = max over p in P of (share of F's sampled members whose
SILVER pillar tags include p). High = the repo's distinguishing marks
are the family business (representative member); low = distinctive.
Computed from data/sample.jsonl + published standards only.
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from standards import disp_rule, pillar_silver, pillar_nameonly, ANCHORS

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data"
sample = {json.loads(l)["name"]: json.loads(l) for l in open(D / "sample.jsonl")}
big = {json.loads(l)["name"]: json.loads(l) for l in open(D / "big_labels.jsonl")}
algo = {json.loads(l)["name"]: json.loads(l) for l in open(D / "decisions_algo.jsonl")}

WORD = re.compile(r"[a-z0-9]+")
def words(t): return set(WORD.findall((t or "").lower()))
fam_members = defaultdict(list)
for name, r in sample.items(): fam_members[r["gold_family"]].append(name)
silver = {n: pillar_silver(n, sample[n].get("d")) for n in sample}
algopil = {n: algo[n]["PILLAR"] for n in sample}

def typicality(name, pillars, tag_source):
    fam = sample[name]["gold_family"]
    if fam == "OTHER" or not pillars: return None
    ms = fam_members[fam]
    return max(sum(1 for m in ms if p in tag_source[m]) / len(ms) for p in pillars)

def centroid_ovl(name):
    fam = sample[name]["gold_family"]
    if fam == "OTHER": return None
    c = Counter()
    for m in fam_members[fam]:
        if m != name:
            for w in words(sample[m].get("d")): c[w] += 1
    cen = {w for w, k in c.items() if k >= 2}
    dw = words(sample[name].get("d"))
    return (len(dw & cen) / len(dw)) if dw else None

def mk(phi=None, theta=None, tags=silver, cells="big"):
    def pred(name):
        if cells == "big":
            b = big[name]; fam, pil = b["FAM"], b["PILLAR"]
        else:
            fam, pil = algo[name]["FAM"], algo[name]["PILLAR"]
        p = disp_rule(fam, pil, name, sample[name]["fork"])
        if p != "DEEP" or fam == "OTHER" or name.lower() in ANCHORS: return p
        if phi is not None:
            t = typicality(name, pil, tags)
            if t is not None and t >= phi: return "COLLAPSE"
        if theta is not None:
            o = centroid_ovl(name)
            if o is not None and o >= theta: return "COLLAPSE"
        return p
    return pred

def report(label, pred, names):
    ok = sum(1 for n in names if pred(n) == big[n]["DISP"])
    flips = [(n, pred(n), big[n]["DISP"]) for n in names
             if pred(n) != (disp_rule(big[n]["FAM"], big[n]["PILLAR"], n, sample[n]["fork"]) if pred != base else big[n]["DISP"])]
    print(f"{label}: {ok}/{len(names)} = {ok/len(names):.1%}")
    return ok

base = mk()
ALL = sorted(big)
def flips_of(pred):
    out = []
    for n in ALL:
        bp = base(n)
        if pred(n) != bp:
            out.append((n, bp, pred(n), big[n]["DISP"],
                        "FIX" if pred(n) == big[n]["DISP"] else "BREAK"))
    return out

print("=== flip accounting (perfect-input chain, n=119) ===")
for label, pred in [("V3 phi=0.30", mk(phi=0.30)),
                    ("V1 theta=0.30", mk(theta=0.30)),
                    ("V3+V1 phi=0.30 theta=0.30", mk(phi=0.30, theta=0.30))]:
    ok = sum(1 for n in ALL if pred(n) == big[n]["DISP"])
    fl = flips_of(pred)
    fx = sum(1 for x in fl if x[4] == "FIX"); br = sum(1 for x in fl if x[4] == "BREAK")
    print(f"{label}: {ok}/119 = {ok/119:.1%}  flips={len(fl)} fixes={fx} breaks={br}")
    for x in fl: print(f"    {x[4]:5s} {x[0]:28s} {x[1]}->{x[2]} (ref {x[3]})")

print("\n=== split-half for the combination (tune phi,theta jointly on tune half) ===")
A, B = ALL[::2], ALL[1::2]
grid = [(p, t) for p in (0.25, 0.30, 0.40) for t in (0.25, 0.30, 0.35)]
for label, tune, test in (("tune A -> test B", A, B), ("tune B -> test A", B, A)):
    def acc_on(pred, ns): return sum(1 for n in ns if pred(n) == big[n]["DISP"]) / len(ns)
    best = max(grid, key=lambda g: acc_on(mk(phi=g[0], theta=g[1]), tune))
    bp = mk(phi=best[0], theta=best[1])
    print(f"{label}: best(phi,theta)={best} tune={acc_on(bp, tune):.1%} test={acc_on(bp, test):.1%} "
          f"(base on test {acc_on(base, test):.1%})")

print("\n=== production chain (ALGO cells; REP from ALGO tags, phi=0.30) ===")
prod_base = lambda n: disp_rule(algo[n]["FAM"], algo[n]["PILLAR"], n, sample[n]["fork"])
prod_rep = mk(phi=0.30, tags=algopil, cells="algo")
for label, pred in (("ALGO-chain base", prod_base), ("ALGO-chain + REP", prod_rep)):
    ok = sum(1 for n in ALL if pred(n) == big[n]["DISP"])
    print(f"{label}: {ok}/119 = {ok/119:.1%}  (published ALGO-chain: 78.2%)")

print("\n=== residual after V3+V1 (perfect chain) ===")
pred = mk(phi=0.30, theta=0.30)
res = [(n, pred(n), big[n]["DISP"]) for n in ALL if pred(n) != big[n]["DISP"]]
print(f"{len(res)} errors remain:")
for n, p, r in res: print(f"    {n:32s} pred={p:8s} ref={r}")

# ---- REP values for all 395 ----
rows = []
for name, r in sample.items():
    fam = r["gold_family"]
    typ = typicality(name, silver[name], silver)
    rows.append({"name": name, "family": fam, "fork": r["fork"],
                 "silver_pillars": silver[name],
                 "rep_typicality": None if typ is None else round(typ, 3),
                 "rep_centroid_overlap": None if centroid_ovl(name) is None else round(centroid_ovl(name), 3),
                 "rep_class": ("NA-other" if fam == "OTHER" else
                               "NA-nopillar" if typ is None else
                               "ROUTINE" if typ >= 0.30 else "DISTINCT")})
with open(D / "rep_values.jsonl", "w") as f:
    for row in rows: f.write(json.dumps(row) + "\n")
print("\nREP for 395 written to data/rep_values.jsonl; class mix:",
      dict(Counter(r["rep_class"] for r in rows)))

#!/usr/bin/env python3
"""Score all tiers against all standards. Emits data/scores.json + prints tables.
Standards: GOLD (programmatic family), SILVER (keyword rules), REF (BIG labels).
SMALL metrics are computed ONLY on instances MiniMax actually answered
before the provider 429 hard-stop; n is always printed."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from standards import pillar_silver, disp_rule

D = Path(__file__).resolve().parents[1] / "data"
sample = {json.loads(l)["name"]: json.loads(l) for l in open(f"{D}/sample.jsonl")}
algo = {json.loads(l)["name"]: json.loads(l) for l in open(f"{D}/decisions_algo.jsonl")}
big = {json.loads(l)["name"]: json.loads(l) for l in open(f"{D}/big_labels.jsonl")}
def load_small(cell):
    d = {}
    try:
        for l in open(f"{D}/small_{cell}.jsonl"):
            o = json.loads(l)
            if o["v"] != "MISSING": d[o["name"]] = o["v"]
    except FileNotFoundError: pass
    return d
small = {c: load_small(c) for c in ["FAM","TRAP","PILLAR"]}

def acc(pairs):
    pairs = [(a,b) for a,b in pairs if a is not None]
    if not pairs: return (0, 0, 0.0)
    ok = sum(1 for a,b in pairs if a == b)
    return (ok, len(pairs), ok/len(pairs))

def setmatch(a, b):  # pillar sets
    return set(a or []) == set(b or [])
def overlap(a, b):
    a, b = set(a or []), set(b or [])
    return bool(a & b) or (not a and not b)

S = {}
names = list(sample)

# ---------- FAM ----------
S["FAM_ALGO_vs_GOLD"] = acc([(algo[n]["FAM"], sample[n]["gold_family"]) for n in names])
S["FAM_SMALL_vs_GOLD"] = acc([(small["FAM"].get(n), sample[n]["gold_family"]) for n in names])
S["FAM_BIG_vs_GOLD"] = acc([(big[n]["FAM"], sample[n]["gold_family"]) for n in big])
S["FAM_SMALL_fidelity_BIG"] = acc([(small["FAM"].get(n), big[n]["FAM"]) for n in big])
S["FAM_ALGO_fidelity_BIG"] = acc([(algo[n]["FAM"], big[n]["FAM"]) for n in big])
byst = defaultdict(list)
for n in names: byst[sample[n]["stratum"]].append(n)
S["FAM_SMALL_vs_GOLD_by_stratum"] = {k: acc([(small["FAM"].get(n), sample[n]["gold_family"]) for n in v]) for k, v in byst.items()}
S["FAM_SMALL_errors"] = [(n, small["FAM"][n], sample[n]["gold_family"], sample[n]["stratum"])
                         for n in names if n in small["FAM"] and small["FAM"][n] != sample[n]["gold_family"]][:40]

# ---------- TRAP ----------
S["TRAP_REF_base"] = Counter(big[n]["TRAP"] for n in big)
S["TRAP_SMALL_vs_REF"] = acc([(small["TRAP"].get(n), big[n]["TRAP"]) for n in big])
S["TRAP_ALGO_vs_REF"] = acc([(algo[n]["TRAP"], big[n]["TRAP"]) for n in big])
S["TRAP_SMALL_confusion"] = Counter((big[n]["TRAP"], small["TRAP"][n]) for n in big if n in small["TRAP"])
S["TRAP_ALGO_confusion"] = Counter((big[n]["TRAP"], algo[n]["TRAP"]) for n in big)
S["TRAP_SMALL_vs_ALGO_agree"] = acc([(small["TRAP"].get(n), algo[n]["TRAP"]) for n in names])

# ---------- PILLAR ----------
silv = {n: pillar_silver(n, sample[n].get("d")) for n in names}
def pmetrics(decmap, stdmap, keys):
    ex = [(decmap.get(k), stdmap[k]) for k in keys if decmap.get(k) is not None]
    exact = sum(1 for a,b in ex if setmatch(a,b)); ov = sum(1 for a,b in ex if overlap(a,b))
    return {"n": len(ex), "exact": exact, "exact_rate": exact/len(ex) if ex else 0,
            "overlap": ov, "overlap_rate": ov/len(ex) if ex else 0}
S["PILLAR_ALGO_vs_SILVER"] = pmetrics({n: algo[n]["PILLAR"] for n in names}, silv, names)
S["PILLAR_SMALL_vs_SILVER"] = pmetrics(small["PILLAR"], silv, names)
S["PILLAR_BIG_vs_SILVER"] = pmetrics({n: big[n]["PILLAR"] for n in big}, silv, list(big))
S["PILLAR_SMALL_vs_REF"] = pmetrics(small["PILLAR"], {n: big[n]["PILLAR"] for n in big}, list(big))
S["PILLAR_REF_base"] = Counter(p for n in big for p in big[n]["PILLAR"])
S["PILLAR_SILVER_base"] = Counter(p for n in names for p in silv[n])

# ---------- DISP ----------
silv_disp = {n: disp_rule(sample[n]["gold_family"], silv[n], n, sample[n]["fork"]) for n in names}
S["DISP_ALGO_vs_SILVER"] = acc([(algo[n]["DISP"], silv_disp[n]) for n in names])
S["DISP_ALGO_vs_REF"] = acc([(algo[n]["DISP"], big[n]["DISP"]) for n in big])
S["DISP_SILVER_vs_REF"] = acc([(silv_disp[n], big[n]["DISP"]) for n in big])
# mis-cut probe: formula over BIG's own FAM/PILLAR vs BIG's DISP
S["DISP_formula_on_BIG_cells_vs_REF"] = acc([
    (disp_rule(big[n]["FAM"], big[n]["PILLAR"], n, sample[n]["fork"]), big[n]["DISP"]) for n in big])
S["DISP_REF_base"] = Counter(big[n]["DISP"] for n in big)

Sj = {k: ({str(kk): vv for kk, vv in v.items()} if isinstance(v, Counter) else v) for k, v in S.items()}
json.dump(Sj, open(f"{D}/scores.json", "w"), indent=1, default=str)
for k, v in S.items():
    print(k, ":", v)

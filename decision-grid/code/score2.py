#!/usr/bin/env python3
"""Re-run scoring: all run-1 metrics recomputed on the COMPLETED SMALL
tier, plus the new measurements:
  * SMALL DISP direct + formula chained on SMALL cells (vs REF/SILVER)
  * SUBSTANCE cell: disp_rule v2 (v2a stub-downgrade, v2b pattern-upgrade,
    both) fed BIG's perfect FAM/PILLAR + SMALL's SUBSTANCE, vs REF —
    does the 80.7% ceiling move?
  * TRAP re-cut: SMALL COLLISION / VAGUE vs REF2 hand labels (accuracy,
    always-NO floor, flag precision/recall).
Emits data/scores2.json and prints tables."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from standards import pillar_silver, disp_rule, ANCHORS

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
small = {c: load_small(c) for c in ["FAM", "TRAP", "PILLAR", "DISP"]}
subst = load_small("SUBSTANCE")
recut_ref = {json.loads(l)["name"]: json.loads(l) for l in open(f"{D}/trap_recut_labels.jsonl")}
small_col = load_small("COLLISION")
small_vag = load_small("VAGUE")

def acc(pairs):
    pairs = [(a, b) for a, b in pairs if a is not None]
    if not pairs: return (0, 0, 0.0)
    ok = sum(1 for a, b in pairs if a == b)
    return (ok, len(pairs), round(ok / len(pairs), 4))
def setmatch(a, b): return set(a or []) == set(b or [])
def overlap(a, b):
    a, b = set(a or []), set(b or [])
    return bool(a & b) or (not a and not b)
def pmetrics(decmap, stdmap, keys):
    ex = [(decmap.get(k), stdmap[k]) for k in keys if decmap.get(k) is not None]
    exn = sum(1 for a, b in ex if setmatch(a, b)); ov = sum(1 for a, b in ex if overlap(a, b))
    return {"n": len(ex), "exact": exn, "exact_rate": round(exn / len(ex), 4) if ex else 0,
            "overlap": ov, "overlap_rate": round(ov / len(ex), 4) if ex else 0}

S = {}
names = list(sample)
S["coverage"] = {c: len(small[c]) for c in small}

# ---------- FAM ----------
S["FAM_ALGO_vs_GOLD"] = acc([(algo[n]["FAM"], sample[n]["gold_family"]) for n in names])
S["FAM_SMALL_vs_GOLD"] = acc([(small["FAM"].get(n), sample[n]["gold_family"]) for n in names])
S["FAM_BIG_vs_GOLD"] = acc([(big[n]["FAM"], sample[n]["gold_family"]) for n in big])
S["FAM_SMALL_fidelity_BIG"] = acc([(small["FAM"].get(n), big[n]["FAM"]) for n in big])
S["FAM_ALGO_fidelity_BIG"] = acc([(algo[n]["FAM"], big[n]["FAM"]) for n in big])
byst = defaultdict(list)
for n in names: byst[sample[n]["stratum"]].append(n)
S["FAM_SMALL_vs_GOLD_by_stratum"] = {k: acc([(small["FAM"].get(n), sample[n]["gold_family"]) for n in v]) for k, v in byst.items()}

# ---------- TRAP (original cut) ----------
S["TRAP_REF_base"] = dict(Counter(big[n]["TRAP"] for n in big))
S["TRAP_SMALL_vs_REF"] = acc([(small["TRAP"].get(n), big[n]["TRAP"]) for n in big])
S["TRAP_ALGO_vs_REF"] = acc([(algo[n]["TRAP"], big[n]["TRAP"]) for n in big])
S["TRAP_SMALL_confusion"] = {str(k): v for k, v in Counter((big[n]["TRAP"], small["TRAP"][n]) for n in big if n in small["TRAP"]).items()}
S["TRAP_SMALL_vs_ALGO_agree"] = acc([(small["TRAP"].get(n), algo[n]["TRAP"]) for n in names])
susp = [(big[n]["TRAP"], small["TRAP"][n]) for n in big if n in small["TRAP"]]
flags = [1 for r, s in susp if s == "SUSPECT"]
S["TRAP_SMALL_flag_precision"] = (sum(1 for r, s in susp if s == "SUSPECT" and r == "SUSPECT"),
                                  len(flags), round(sum(1 for r, s in susp if s == "SUSPECT" and r == "SUSPECT") / len(flags), 4) if flags else 0)

# ---------- PILLAR ----------
silv = {n: pillar_silver(n, sample[n].get("d")) for n in names}
S["PILLAR_ALGO_vs_SILVER"] = pmetrics({n: algo[n]["PILLAR"] for n in names}, silv, names)
S["PILLAR_SMALL_vs_SILVER"] = pmetrics(small["PILLAR"], silv, names)
S["PILLAR_BIG_vs_SILVER"] = pmetrics({n: big[n]["PILLAR"] for n in big}, silv, list(big))
S["PILLAR_SMALL_vs_REF"] = pmetrics(small["PILLAR"], {n: big[n]["PILLAR"] for n in big}, list(big))
S["PILLAR_ALGO_vs_REF"] = pmetrics({n: algo[n]["PILLAR"] for n in big}, {n: big[n]["PILLAR"] for n in big}, list(big))
S["PILLAR_SMALL_base"] = dict(Counter(p for n in small["PILLAR"] for p in (small["PILLAR"][n] or [])))
S["PILLAR_REF_base"] = dict(Counter(p for n in big for p in big[n]["PILLAR"]))
S["PILLAR_AGREE_SMALL_ALGO"] = pmetrics(small["PILLAR"], {n: algo[n]["PILLAR"] for n in names}, names)
S["PILLAR_AGREE_SMALL_SILVERorALGO"] = {}
both = {}
for n in names:
    a, s = set(algo[n]["PILLAR"] or []), set(silv[n] or [])
    both[n] = sorted(a | s)
S["PILLAR_SMALL_vs_ALGOorSILVER"] = pmetrics(small["PILLAR"], both, names)

# ---------- DISP ----------
silv_disp = {n: disp_rule(sample[n]["gold_family"], silv[n], n, sample[n]["fork"]) for n in names}
S["DISP_REF_base"] = dict(Counter(big[n]["DISP"] for n in big))
S["DISP_ALGO_vs_SILVER"] = acc([(algo[n]["DISP"], silv_disp[n]) for n in names])
S["DISP_ALGO_vs_REF"] = acc([(algo[n]["DISP"], big[n]["DISP"]) for n in big])
S["DISP_SILVER_vs_REF"] = acc([(silv_disp[n], big[n]["DISP"]) for n in big])
S["DISP_formula_on_BIG_cells_vs_REF"] = acc([
    (disp_rule(big[n]["FAM"], big[n]["PILLAR"], n, sample[n]["fork"]), big[n]["DISP"]) for n in big])
S["DISP_SMALL_vs_REF"] = acc([(small["DISP"].get(n), big[n]["DISP"]) for n in big])
S["DISP_SMALL_vs_SILVER"] = acc([(small["DISP"].get(n), silv_disp[n]) for n in names])
S["DISP_formula_on_SMALL_cells_vs_REF"] = acc([
    (disp_rule(small["FAM"].get(n), small["PILLAR"].get(n), n, sample[n]["fork"]), big[n]["DISP"])
    for n in big if small["FAM"].get(n) is not None and small["PILLAR"].get(n) is not None])
S["DISP_SMALL_confusion"] = {str(k): v for k, v in Counter((big[n]["DISP"], small["DISP"][n]) for n in big if n in small["DISP"]).items()}

# ---------- SUBSTANCE / DISP v2 ----------
def disp_v2(family, pillars, name, fork, substance, use_a=True, use_b=True, silv_p=None):
    base = disp_rule(family, pillars, name, fork)
    if use_a and base == "DEEP" and substance == "STUB" and name.lower() not in ANCHORS:
        return "TAIL"
    if use_b and base in ("TAIL", "COLLAPSE") and substance == "SUBSTANTIVE" and silv_p:
        return "DEEP"
    return base
S["SUBSTANCE_SMALL_base_on_REF"] = dict(Counter(subst.get(n) for n in big))
sub_names = [n for n in big if n in subst]
S["DISP_v2a_on_BIG_cells+SMALL_SUBST_vs_REF"] = acc([
    (disp_v2(big[n]["FAM"], big[n]["PILLAR"], n, sample[n]["fork"], subst[n], True, False), big[n]["DISP"]) for n in sub_names])
S["DISP_v2b_on_BIG_cells+SMALL_SUBST_vs_REF"] = acc([
    (disp_v2(big[n]["FAM"], big[n]["PILLAR"], n, sample[n]["fork"], subst[n], False, True, silv[n]), big[n]["DISP"]) for n in sub_names])
S["DISP_v2_on_BIG_cells+SMALL_SUBST_vs_REF"] = acc([
    (disp_v2(big[n]["FAM"], big[n]["PILLAR"], n, sample[n]["fork"], subst[n], True, True, silv[n]), big[n]["DISP"]) for n in sub_names])
# where does the base rule err, and does SUBSTANCE point the right way?
errs = []
for n in sub_names:
    base = disp_rule(big[n]["FAM"], big[n]["PILLAR"], n, sample[n]["fork"])
    if base != big[n]["DISP"]:
        errs.append({"name": n, "base": base, "ref": big[n]["DISP"],
                     "substance": subst[n], "silver_pillars": silv[n],
                     "v2": disp_v2(big[n]["FAM"], big[n]["PILLAR"], n, sample[n]["fork"], subst[n], True, True, silv[n])})
S["DISP_base_errors_with_SUBSTANCE"] = errs
S["DISP_v2_fixes"] = sum(1 for e in errs if e["v2"] == e["ref"])
S["DISP_v2_breaks"] = sum(1 for n in sub_names
    if disp_rule(big[n]["FAM"], big[n]["PILLAR"], n, sample[n]["fork"]) == big[n]["DISP"]
    and disp_v2(big[n]["FAM"], big[n]["PILLAR"], n, sample[n]["fork"], subst[n], True, True, silv[n]) != big[n]["DISP"])

# ---------- TRAP re-cut ----------
def binary_metrics(decmap, refmap, field):
    keys = [n for n in refmap if n in decmap]
    pairs = [(refmap[n][field], decmap[n]) for n in keys]
    a = acc(pairs)
    yes_ref = sum(1 for r, _ in pairs if r == "YES")
    flags = [(r, s) for r, s in pairs if s == "YES"]
    prec = (sum(1 for r, s in flags if r == "YES"), len(flags),
            round(sum(1 for r, s in flags if r == "YES") / len(flags), 4) if flags else 0)
    caught = sum(1 for r, s in pairs if r == "YES" and s == "YES")
    floor = (len(pairs) - yes_ref, len(pairs), round((len(pairs) - yes_ref) / len(pairs), 4))
    return {"n": len(pairs), "accuracy": a, "ref_YES": yes_ref,
            "floor_always_NO": floor, "flag_precision": prec,
            "recall_YES": (caught, yes_ref, round(caught / yes_ref, 4) if yes_ref else 0)}
S["COLLISION_SMALL_vs_REF2"] = binary_metrics(small_col, recut_ref, "COLLISION")
S["VAGUE_SMALL_vs_REF2"] = binary_metrics(small_vag, recut_ref, "VAGUE")
S["COLLISION_SMALL_disagreements"] = [n for n in recut_ref if n in small_col and small_col[n] != recut_ref[n]["COLLISION"]]
S["VAGUE_SMALL_disagreements"] = [n for n in recut_ref if n in small_vag and small_vag[n] != recut_ref[n]["VAGUE"]]

json.dump(S, open(f"{D}/scores2.json", "w"), indent=1, default=str)
for k, v in S.items():
    print(k, ":", v)

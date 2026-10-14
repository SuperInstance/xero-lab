#!/usr/bin/env python3
"""REP study, phase 1: reproduce the DISP ceiling and dissect its errors.

Read-only against the published grid data/code. Imports disp_rule from
the published standards.py; writes nothing into data/ (prints only).
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from standards import disp_rule, ANCHORS

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data"
sample = {json.loads(l)["name"]: json.loads(l) for l in open(D / "sample.jsonl")}
big = {json.loads(l)["name"]: json.loads(l) for l in open(D / "big_labels.jsonl")}
subst = {json.loads(l)["name"]: json.loads(l)["v"] for l in open(D / "small_SUBSTANCE.jsonl")}

# ---- reproduce base: disp_rule over BIG (perfect) FAM/PILLAR vs REF DISP ----
conf = Counter()
errors = []
for name, b in big.items():
    pred = disp_rule(b["FAM"], b["PILLAR"], name, sample[name]["fork"])
    conf[(pred, b["DISP"])] += 1
    if pred != b["DISP"]:
        errors.append((name, pred, b["DISP"]))
ok = sum(v for (p, r), v in conf.items() if p == r)
print(f"BASE formula on BIG cells: {ok}/{len(big)} = {ok/len(big):.1%}  (published ceiling: 80.7%)")
print("confusion (pred, ref):", dict(sorted(conf.items())))
print(f"errors: {len(errors)}")
by_class = Counter((p, r) for _, p, r in errors)
for k, v in sorted(by_class.items()):
    print(f"  {k[0]} -> {k[1]}: {v}")

# ---- candidate REP features (name/desc/fork/family only) ----
WORD = re.compile(r"[a-z0-9]+")
def words(text): return set(WORD.findall((text or "").lower()))
def toks(name): return re.split(r"[-_.]", name.lower())

# family description centroids within the 395 sample (per GOLD family)
fam_words = defaultdict(Counter)
fam_members = defaultdict(list)
for name, r in sample.items():
    fam_members[r["gold_family"]].append(name)
    for w in words(r.get("d")):
        fam_words[r["gold_family"]][w] += 1

def features(name):
    r = sample[name]
    fam = r["gold_family"]
    t = toks(name)
    fam_size = len(fam_members[fam]) if fam != "OTHER" else 0
    dw = words(r.get("d"))
    centroid = {w for w, c in fam_words[fam].items() if c >= 2} if fam != "OTHER" else set()
    overlap = len(dw & centroid) / max(1, len(dw)) if dw else 0.0
    return {
        "fam": fam, "fam_n_sample": fam_size, "fork": r["fork"],
        "stratum": r["stratum"], "lang": r["l"],
        "bare_family_name": fam != "OTHER" and name.lower() == fam,
        "lead_token_is_family": bool(t) and t[0] == fam,
        "fused_family": fam != "OTHER" and t[0] != fam and name.lower().startswith(fam),
        "n_tokens": len(t),
        "desc_words": len(dw),
        "desc_centroid_overlap": round(overlap, 2),
        "anchor": name.lower() in ANCHORS,
        "subst": subst.get(name),
    }

print("\n--- the 23 base errors, with candidate features ---")
for name, pred, ref in sorted(errors, key=lambda e: (e[1], e[2], e[0])):
    f = features(name)
    b = big[name]
    print(f"{name:32s} pred={pred:8s} ref={ref:8s} FAM={b['FAM']:12s} PIL={'+'.join(b['PILLAR']) or '-':28s} "
          f"fork={f['fork']!s:5s} stratum={f['stratum']:9s} bare={f['bare_family_name']!s:5s} "
          f"lead={f['lead_token_is_family']!s:5s} fused={f['fused_family']!s:5s} ntok={f['n_tokens']} "
          f"descw={f['desc_words']:3d} ovl={f['desc_centroid_overlap']:.2f} subst={f['subst']}")

print("\n--- correct DEEP calls (the control group REP must not break) ---")
n_deep_ok = 0
for name, b in big.items():
    pred = disp_rule(b["FAM"], b["PILLAR"], name, sample[name]["fork"])
    if pred == "DEEP" and b["DISP"] == "DEEP":
        n_deep_ok += 1
        f = features(name)
        print(f"{name:32s} FAM={b['FAM']:12s} PIL={'+'.join(b['PILLAR']) or '-':28s} fork={f['fork']!s:5s} "
              f"stratum={f['stratum']:9s} bare={f['bare_family_name']!s:5s} lead={f['lead_token_is_family']!s:5s} "
              f"fused={f['fused_family']!s:5s} ntok={f['n_tokens']} descw={f['desc_words']:3d} ovl={f['desc_centroid_overlap']:.2f} subst={f['subst']}")
print("correct DEEP:", n_deep_ok)

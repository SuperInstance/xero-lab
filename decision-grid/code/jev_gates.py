#!/usr/bin/env python3
"""Jev gate work: (a) calibration calls that set gate policy from measured
evidence; (b) per-instance gates on SMALL decisions in the BIG subsample.
Every call is logged to data/jev_calls.jsonl. Mapping: p>=0.70 ACCEPT (pos),
0.40<p<0.70 ESCALATE (zero/deadband), p<=0.40 REJECT (neg; redo by BIG)."""
import json, subprocess, random, sys, os
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "data"
# The Jev CLI (jev.py, TypeSafe skill) is an external tool, not part of
# this repo. Its committed results live in data/jev_calls.jsonl and
# data/jev_instance_results.json.
JEV = os.environ.get("JEV_CLI")
if not JEV or not os.path.exists(JEV):
    sys.exit("jev_gates.py needs the Jev gate CLI (jev.py). It is not in "
             "this repo — point JEV_CLI at it:\n"
             "  JEV_CLI=/path/to/jev.py python3 code/jev_gates.py\n"
             "Everything else in the pipeline runs from the committed "
             "data without it.")
random.seed(4242)
LOG = open(f"{D}/jev_calls.jsonl", "a")

def jev_noul(context, question, tgloss, fgloss):
    r = subprocess.run(["python3", JEV, "noul", context, question,
                        "--true", tgloss, "--false", fgloss],
                       capture_output=True, text=True, timeout=120)
    out = json.loads(r.stdout)
    return out["noul"]

def jev_choice(context, question, options):
    args = ["python3", JEV, "choice", context, question] + [f"{k}={v}" for k, v in options.items()]
    r = subprocess.run(args, capture_output=True, text=True, timeout=120)
    return json.loads(r.stdout)

def log(kind, cell, target, context, question, verdict):
    LOG.write(json.dumps({"kind": kind, "cell": cell, "target": target,
                          "context": context, "question": question,
                          "verdict": verdict}) + "\n")
    LOG.flush()

# ---------------- (a) calibration ----------------
EVID = ("Validation evidence from the decision-grid run (395 SuperInstance repos, "
        "119 with strong-model reference labels): the first-token naming rule matches "
        "strong-model family labels 98.3% of the time; a small LLM reproduces them 91.2%. "
        "The small model over-flags misleading names: of its SUSPECT flags only ~6% were "
        "confirmed; the true SUSPECT base rate is 3.4%. A keyword silver standard for "
        "pillar tags fires 'pyramid-orchestration' 76 times where the strong model found 6. "
        "A disposition formula fed perfect FAM/PILLAR inputs reproduces strong-model "
        "dispositions only 80.7% of the time.")
CAL = [
 ("FAM", "rule: big-family cells staffed by naming rule alone",
  "Should family-classification cells for repos in large name-families be staffed by the naming rule alone, with no model call?",
  "the naming rule is reliable enough to staff these cells alone",
  "these cells still need a model decision"),
 ("FAM", "rule: fused-name tail repos escalate",
  "For tail repos whose names fuse a family word without a separator (e.g. 'jeviter'), should the cell escalate to the big tier instead of trusting the token rule?",
  "fused-name cases should escalate", "the token rule handles them fine"),
 ("TRAP", "rule: SUSPECT flags are watches, not verdicts",
  "Should SUSPECT flags from cheap deciders be treated as watches that escalate for confirmation, never as final verdicts?",
  "flags are too unreliable to be verdicts; escalate them",
  "flags are reliable enough to stand as verdicts"),
 ("PILLAR", "rule: keyword pillar tags are candidates, not finals",
  "Should keyword-based pillar tags be treated as candidates requiring confirmation rather than final tags?",
  "keyword tags over-fire and need confirmation",
  "keyword tags are accurate enough to be final"),
 ("DISP", "rule: disposition by formula by default, escalate pillar-bearing tail/fork",
  "Should disposition be computed by formula by default, escalating only pillar-bearing tail or fork repos to the big tier?",
  "formula-by-default with targeted escalation is the right staffing",
  "disposition needs a model decision on every repo"),
 ("NODESC", "rule: no-description repos escalate semantic cells",
  "For repos with no description, should semantic cells (name-honesty, pillar tags) escalate by default because there is no evidence to decide from?",
  "no-evidence cells should escalate by default",
  "names alone are enough for these cells"),
 ("GATE", "rule: tier disagreement alone triggers escalation",
  "Is disagreement between the algorithmic decider and the small model, by itself, a sufficient trigger to escalate a cell to the big tier?",
  "disagreement alone is a sufficient escalation trigger",
  "disagreement alone is not sufficient; more signal is needed"),
]
for cell, target, q, tg, fg in CAL:
    p = jev_noul(EVID, q, tg, fg)
    band = "pos" if p >= 0.70 else ("neg" if p <= 0.40 else "zero")
    log("calibration", cell, target, EVID, q, {"p_true": p, "band": band})
    print("CAL", cell, target[:40], "p=", p, band, flush=True)

opts = {"disagreements": "escalate cells where the cheap deciders disagree with each other",
        "deep_candidates": "escalate only cells whose outcome is expensive (DEEP dispositions, SUSPECT flags)",
        "no_evidence": "escalate only cells with no description to decide from",
        "fused_names": "escalate only naming-rule edge cases (fused family words, collisions)"}
v = jev_choice(EVID, "Where should the grid spend its limited big-tier escalation budget?", opts)
log("calibration", "ALL", "choice: escalation budget allocation", EVID,
    "Where should the grid spend its limited big-tier escalation budget?", v)
print("CAL choice:", v, flush=True)

# ---------------- (b) instance gates ----------------
sample = {json.loads(l)["name"]: json.loads(l) for l in open(f"{D}/sample.jsonl")}
big = {json.loads(l)["name"]: json.loads(l) for l in open(f"{D}/big_labels.jsonl")}
def load_small(cell):
    d = {}
    for l in open(f"{D}/small_{cell}.jsonl"):
        o = json.loads(l)
        if o["v"] != "MISSING": d[o["name"]] = o["v"]
    return d
def band_of(p): return "pos" if p >= 0.70 else ("neg" if p <= 0.40 else "zero")

results = []
for cell, n_dis, n_agr in [("FAM", 6, 12), ("TRAP", 12, 6)]:
    sm = load_small(cell)
    cands = [n for n in big if n in sm]
    dis = [n for n in cands if sm[n] != big[n][cell]]
    agr = [n for n in cands if sm[n] == big[n][cell]]
    random.shuffle(dis); random.shuffle(agr)
    picks = [(n, "disagreement") for n in dis[:n_dis]] + [(n, "agreement-control") for n in agr[:n_agr]]
    for name, why in picks:
        r = sample[name]
        ctx = (f"Repo: {name}. Description: {(r.get('d') or '(no description)')[:220]}. "
               f"Language: {r.get('l') or '-'}. Fork: {r['fork']}.")
        if cell == "FAM":
            ctx += (f" The naming rule assigns family '{r['gold_family']}'. "
                    f"A small model classified this repo's survey family as '{sm[name]}'.")
            q = "Is the small model's family classification the right one for this repo?"
            tg, fg = "the small model's family matches what this repo is", "the small model's family is wrong for this repo"
        else:
            ctx += (f" A small model judged this repo's name as '{sm[name]}' "
                    f"(TRUST = the name honestly signals the content; SUSPECT = the name misleads).")
            q = "Is the small model's judgment about this repo's name correct?"
            tg, fg = "the small model's name judgment is correct", "the small model's name judgment is wrong"
        p = jev_noul(ctx, q, tg, fg)
        band = band_of(p)
        correct_small = (sm[name] == big[name][cell])
        final = sm[name] if band == "pos" else big[name][cell]
        results.append({"cell": cell, "name": name, "picked": why, "p": p, "band": band,
                        "small": sm[name], "ref": big[name][cell],
                        "small_correct": correct_small, "final_correct": final == big[name][cell]})
        log("instance", cell, name, ctx, q, {"p_true": p, "band": band})
        print("INST", cell, name, "p=", p, band, "small_correct=", correct_small, flush=True)

json.dump(results, open(f"{D}/jev_instance_results.json", "w"), indent=1)
LOG.close()
print("instance gates done:", len(results))

#!/usr/bin/env python3
"""Re-run Jev gate calls. Reads a plan (data/jev_rerun_plan.json): a list
of {kind: noul|choice, cell, target, context, question, true, false} or
{kind: choice, options:{key:gloss}}. Executes sequentially, appends every
call to data/jev_calls.jsonl in the run-1 format, prints verdicts.
Band mapping (same as run 1): p>=0.70 pos, 0.40<p<0.70 zero, p<=0.40 neg."""
import json, subprocess, sys, os
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "data"
# The Jev CLI (jev.py, TypeSafe skill) is an external tool, not part of
# this repo. Its committed re-run results live in
# data/jev_rerun_results.json.
JEV = os.environ.get("JEV_CLI")
if not JEV or not os.path.exists(JEV):
    sys.exit("jev_rerun.py needs the Jev gate CLI (jev.py). It is not in "
             "this repo — point JEV_CLI at it:\n"
             "  JEV_CLI=/path/to/jev.py python3 code/jev_rerun.py\n"
             "Everything else in the pipeline runs from the committed "
             "data without it.")

def jev_noul(context, question, tgloss, fgloss):
    r = subprocess.run(["python3", JEV, "noul", context, question,
                        "--true", tgloss, "--false", fgloss],
                       capture_output=True, text=True, timeout=120)
    return json.loads(r.stdout)["noul"]

def jev_choice(context, question, options):
    args = ["python3", JEV, "choice", context, question] + [f"{k}={v}" for k, v in options.items()]
    r = subprocess.run(args, capture_output=True, text=True, timeout=120)
    return json.loads(r.stdout)

plan = json.load(open(f"{D}/jev_rerun_plan.json"))
LOG = open(f"{D}/jev_calls.jsonl", "a")
out = []
for c in plan:
    if c["kind"] == "noul":
        p = jev_noul(c["context"], c["question"], c["true"], c["false"])
        band = "pos" if p >= 0.70 else ("neg" if p <= 0.40 else "zero")
        verdict = {"p_true": p, "band": band}
    else:
        verdict = jev_choice(c["context"], c["question"], c["options"])
    LOG.write(json.dumps({"kind": "rerun-" + c["kind"], "cell": c["cell"],
                          "target": c["target"], "context": c["context"],
                          "question": c["question"], "verdict": verdict}) + "\n")
    LOG.flush()
    out.append({"cell": c["cell"], "target": c["target"], "verdict": verdict})
    print("JEV", c["cell"], c["target"][:60], "->", verdict, flush=True)
LOG.close()
json.dump(out, open(f"{D}/jev_rerun_results.json", "w"), indent=1)
print("done:", len(out), "calls")

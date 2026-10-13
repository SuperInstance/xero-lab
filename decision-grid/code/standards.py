#!/usr/bin/env python3
"""Shared standards for the decision grid.

PILLARS: the nine zero-program pillars from the survey brief.
Silver standards: deterministic rules over name+description, built from
SURVEY.md vocabulary. They are SILVER, not gold: crude keyword evidence,
used to score deciders at full-sample scale. The strong-model reference
labels (REF) on the 120-repo subsample are the second standard.
"""
import re

PILLARS = ["agent-as-files","two-logs","gates-deadbands","memory-grid",
           "interface-data-logic","deployment","pyramid-orchestration",
           "walkthroughs-skills","calculator-maker"]

PILLAR_KEYWORDS = {
 "agent-as-files": ["git-native","repo is the agent","repo-first","git agent",
                    "muscle-memory","agent template","fork it, register"],
 "two-logs": ["ledger","append-only","judgment log","provenance","audit trail",
              "record is","activity log","receipt"],
 "gates-deadbands": ["deadband","gate","alarm","watchdog","watcher","threshold",
                     "escalation","canary"],
 "memory-grid": ["memory","rooms","room","tiles","tile","grid","cells","cell",
                 "spreadsheet","rag","vector store","index"],
 "interface-data-logic": ["telegram","bridge","render","interface","a2a",
                          "protocol","bottle","chat ui","discord"],
 "deployment": ["esp32","jetson","uno q","bare metal","edge runtime","hardware",
                "cloudflare worker","sensor","actuator"],
 "pyramid-orchestration": ["fleet","orchestration","swarm","multi-agent",
                           "coordination","vessels","registry","topology"],
 "walkthroughs-skills": ["skill","curriculum","bootcamp","walkthrough","lesson",
                         "tutorial","dojo","training"],
 "calculator-maker": ["syzygy","compiler","codegen","forge","generates code",
                      "build intelligence","decomposition"],
}

ANCHORS = {"zero-poc","zero-innate","zero-bootcamp","xero","xero-lab",
           "question-tree","jev-semantic","constraint-theory-core","git.pp-ng",
           "exocortex-core","cocapn","agent-inbox","edge-ledger"}

def _hits(text, kws):
    return sum(1 for k in kws if k in text)

def pillar_silver(name, desc):
    """Up to 2 pillars by keyword evidence in name+description."""
    text = (name + " " + (desc or "")).lower()
    scored = [(p, _hits(text, kws)) for p, kws in PILLAR_KEYWORDS.items()]
    scored = [(p, h) for p, h in scored if h > 0]
    scored.sort(key=lambda x: -x[1])
    return [p for p, _ in scored[:2]]

def pillar_nameonly(name):
    """ALGO-tier pillar call: name keywords only (weaker by design)."""
    text = name.lower().replace("-", " ").replace("_", " ")
    scored = [(p, _hits(text, [k.replace("-"," ") for k in kws]))
              for p, kws in PILLAR_KEYWORDS.items()]
    scored = [(p, h) for p, h in scored if h > 0]
    scored.sort(key=lambda x: -x[1])
    return [p for p, _ in scored[:2]]

def disp_rule(family, pillars, name, fork):
    """Disposition from cell values, survey practice:
    DEEP = pillar-bearing or anchor; COLLAPSE = plain big-family member;
    TAIL = everything else."""
    if pillars or name.lower() in ANCHORS:
        return "DEEP"
    if family != "OTHER":
        return "COLLAPSE"
    return "TAIL"

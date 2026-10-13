# Judgment log — Jev gates for the decision grid

Every Jev (TypeSafe) call made by the gate layer, 2026-10-13. Band mapping: p ≥ 0.70 → **pos** (accept), 0.40 < p < 0.70 → **zero** (deadband — escalate), p ≤ 0.40 → **neg** (reject, redo by big tier).

Total calls logged: 44 (8 calibration incl. 1 choice, 36 instance gates).

## Calibration calls (gate policy, from measured validation evidence)

| Cell | Gate rule under judgment | p(true) | Band |
|---|---|---|---|
| FAM | rule: big-family cells staffed by naming rule alone | 0.38 | neg |
| FAM | rule: fused-name tail repos escalate | 0.64 | zero |
| TRAP | rule: SUSPECT flags are watches, not verdicts | 0.9 | pos |
| PILLAR | rule: keyword pillar tags are candidates, not finals | 0.96 | pos |
| DISP | rule: disposition by formula by default, escalate pillar-bearing tail/fork | 0.49 | zero |
| NODESC | rule: no-description repos escalate semantic cells | 0.37 | neg |
| GATE | rule: tier disagreement alone triggers escalation | 0.2 | neg |

Choice — escalation budget allocation: **disagreements** (confidence 0.35; probabilities {'disagreements': 0.51, 'deep_candidates': 0.46, 'no_evidence': 0.0, 'fused_names': 0.03}).

## Instance gates (SMALL decisions judged one by one)

| Cell | Repo | Why picked | SMALL | REF (big) | SMALL right? | Jev p | Band | Gated final right? |
|---|---|---|---|---|---|---|---|---|
| FAM | witness-is-prediction | disagreement | substrate | OTHER | NO | 0.49 | zero | yes |
| FAM | crab | disagreement | agent | OTHER | NO | 0.48 | zero | yes |
| FAM | reposphere | disagreement | agent | OTHER | NO | 0.36 | neg | yes |
| FAM | SuperInstance-archive | disagreement | OTHER | superinstance | NO | 0.13 | neg | yes |
| FAM | makerlog-ai-pages | disagreement | ai | OTHER | NO | 0.31 | neg | yes |
| FAM | garden | disagreement | cocapn | OTHER | NO | 0.34 | neg | yes |
| FAM | ternary-cell-python | agreement-control | ternary | ternary | yes | 0.9 | pos | yes |
| FAM | jev-paint-quilt | agreement-control | jev | jev | yes | 0.65 | zero | yes |
| FAM | gossip-seed | agreement-control | OTHER | OTHER | yes | 0.54 | zero | yes |
| FAM | luau-recipe | agreement-control | OTHER | OTHER | yes | 0.45 | zero | yes |
| FAM | plato-room-phi | agreement-control | plato | plato | yes | 0.87 | pos | yes |
| FAM | plato-tile-fountain | agreement-control | plato | plato | yes | 0.74 | pos | yes |
| FAM | agent-motif | agreement-control | agent | agent | yes | 0.66 | zero | yes |
| FAM | ship-log-modules | agreement-control | OTHER | OTHER | yes | 0.53 | zero | yes |
| FAM | fleet-map | agreement-control | fleet | fleet | yes | 0.86 | pos | yes |
| FAM | lau-network-science | agreement-control | lau | lau | yes | 0.64 | zero | yes |
| FAM | ternary-manifesto | agreement-control | ternary | ternary | yes | 0.87 | pos | yes |
| FAM | ternary-mesh | agreement-control | ternary | ternary | yes | 0.89 | pos | yes |
| TRAP | git.pp-ng | disagreement | SUSPECT | TRUST | NO | 0.4 | neg | yes |
| TRAP | zero-knowledge | disagreement | TRUST | SUSPECT | NO | 0.5 | zero | yes |
| TRAP | quilt-fable | disagreement | SUSPECT | TRUST | NO | 0.39 | neg | yes |
| TRAP | lucineer-fleet-wiki | disagreement | SUSPECT | TRUST | NO | 0.56 | zero | yes |
| TRAP | hermes-memory-mcp | disagreement | SUSPECT | TRUST | NO | 0.51 | zero | yes |
| TRAP | lau-state-machine | disagreement | SUSPECT | TRUST | NO | 0.41 | zero | yes |
| TRAP | ternary-manifesto | disagreement | SUSPECT | TRUST | NO | 0.45 | zero | yes |
| TRAP | agent-motif | disagreement | SUSPECT | TRUST | NO | 0.39 | neg | yes |
| TRAP | quiltcall | disagreement | SUSPECT | TRUST | NO | 0.53 | zero | yes |
| TRAP | researchlocal-backup | disagreement | SUSPECT | TRUST | NO | 0.41 | zero | yes |
| TRAP | zero-poc | disagreement | SUSPECT | TRUST | NO | 0.57 | zero | yes |
| TRAP | luciddreamer-content | disagreement | SUSPECT | TRUST | NO | 0.55 | zero | yes |
| TRAP | ternary-phase | agreement-control | TRUST | TRUST | yes | 0.77 | pos | yes |
| TRAP | ternary-tnn | agreement-control | TRUST | TRUST | yes | 0.72 | pos | yes |
| TRAP | ternary-markov | agreement-control | TRUST | TRUST | yes | 0.81 | pos | yes |
| TRAP | ternary-projection | agreement-control | TRUST | TRUST | yes | 0.85 | pos | yes |
| TRAP | graph-planarity | agreement-control | TRUST | TRUST | yes | 0.91 | pos | yes |
| TRAP | plato-room-phi | agreement-control | TRUST | TRUST | yes | 0.57 | zero | yes |

On this disagreement-enriched set (n=36): SMALL alone scored 50%, the Jev-gated pipeline scored 100%. Jev accepted (pos) 11 decisions and every accepted one was correct (accept precision 11/11); no wrong SMALL decision was accepted — every error landed in the zero band (escalate) or neg band (reject). Full contexts and questions for every call: `data/jev_calls.jsonl`.

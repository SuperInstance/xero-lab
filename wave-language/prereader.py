#!/usr/bin/env python3
"""Route A — the deterministic pre-reader (v3).

Algorithms measure; the model (elsewhere) judges. This module wires
the v2 authoring estimators into a standalone instrument that consumes
a sea the way a deployed pre-reader would: the height field (FFT
direction, buoy-peak period, bright-cell trend) plus the SET/LULL
marker channel parsed out of the rendered stream text — the same
channel every reader in v1/v2 was given.

Deliberate differences from authoring.py's teacher tooling:
  - sets are estimated from the marker runs and the ESTIMATED period
    (authoring used the true period to build its worked examples);
  - nothing here is admitted/rejected against ground truth — the
    estimators' raw outputs, including "ambiguous" and "unknown",
    are what get scored and what the judge's brief carries.
"""
import numpy as np
from authoring import buoy_peaks, fft_direction, trend_measure
from render import assemble_stream

DT = 1.25


def parse_markers(stream_text):
    """Per-frame marker list ('SET' / 'LULL' / None) parsed from the
    assembled stream text — the marker channel as rendered."""
    marks = []
    pending = None
    for line in stream_text.splitlines():
        if line == "--- SET ---":
            pending = "SET"
        elif line == "~~~ LULL ~~~":
            pending = "LULL"
        elif line.startswith("[t="):
            marks.append(pending)
            pending = None
    return marks


def sets_estimate(marks, est_period):
    """Waves-per-set from the rendered marker structure, using the
    ESTIMATED period. Mirrors authoring.sets_measure's two honest
    routes ('run', then 'cycle'). Returns (est, info): est is an int,
    the string "none", or None when the window cannot support a call.
    """
    info = {"n_set_markers": marks.count("SET"),
            "n_lull_markers": marks.count("LULL"), "method": None}
    if info["n_lull_markers"] == 0:
        info["method"] = "none"
        return "none", info
    if est_period is None:
        info["method"] = "no-period"
        return None, info
    state = marks[0] == "SET"
    inset = []
    for m in marks:
        if m == "SET":
            state = True
        elif m == "LULL":
            state = False
        inset.append(state)
    runs = []  # (value, start, end_exclusive, touches_left, touches_right)
    s0 = 0
    for i in range(1, len(inset) + 1):
        if i == len(inset) or inset[i] != inset[s0]:
            runs.append((inset[s0], s0, i, s0 == 0, i == len(inset)))
            s0 = i
    complete_sets = [e - s for v, s, e, tl, tr_ in runs if v and not tl and not tr_]
    complete_lulls = [e - s for v, s, e, tl, tr_ in runs if not v and not tl and not tr_]
    if complete_sets:
        med = float(np.median(complete_sets))
        info.update(method="run", run_frames=med)
        return max(1, int(round(med * DT / est_period))), info
    set_starts = [s for v, s, e, tl, tr_ in runs if v and not tl]
    if len(set_starts) >= 2 and complete_lulls:
        cycle = float(np.median(np.diff(set_starts))) * DT
        lull = float(np.median(complete_lulls)) * DT
        info.update(method="cycle", cycle_s=cycle, lull_s=lull)
        return max(1, int(round((cycle - lull) / est_period))), info
    info["method"] = "truncated"
    return None, info


def measure(times, frames, sea):
    """Run every estimator. Returns a measurements dict — the only
    thing route A (alone or with judge) is allowed to know."""
    stream_text = assemble_stream(times, frames, sea.period_s, sea.sets,
                                  "letters", phase0=sea.env_phase0)
    marks = parse_markers(stream_text)
    pk_t, est_T = buoy_peaks(times, frames)
    snap, (kx, ky, lam), frac = fft_direction(frames)
    e, l, rel, klass = trend_measure(frames)
    est_sets, sinfo = sets_estimate(marks, est_T)
    return {
        "direction": snap, "dir_peak_frac": round(float(frac), 3),
        "dir_lambda_m": round(float(lam)),
        "period_s": None if est_T is None else round(float(est_T), 2),
        "n_peaks": len(pk_t),
        "trend_class": klass, "trend_early": round(float(e), 1),
        "trend_late": round(float(l), 1), "trend_rel": round(float(rel), 2),
        "sets": est_sets, "sets_info": sinfo,
    }


def estimator_answer(meas):
    """The estimators' raw outputs in the scorer's answer format.
    'ambiguous' trend and None sets/period are left as-is: they score
    as wrong, which is the honest price of a dead zone."""
    return {"direction": meas["direction"], "period_s": meas["period_s"],
            "trend": meas["trend_class"], "sets": meas["sets"]}


def render_brief(meas):
    """The text brief the judging model receives — measurements only,
    with the instrument's own confidence signals stated plainly."""
    if meas["period_s"] is None:
        period_line = ("Period at the centre buoy: no clear period "
                       f"(only {meas['n_peaks']} crests could be counted).")
    else:
        period_line = (f"Period at the centre buoy: {meas['period_s']:.1f} s "
                       f"({meas['n_peaks']} crests counted).")
    if meas["trend_class"] == "ambiguous":
        trend_line = (f"Trend: the instrument's two statistics disagree "
                      f"(bright cells average {meas['trend_early']:.0f} per frame early, "
                      f"{meas['trend_late']:.0f} late; fitted change {meas['trend_rel']:+.0%}) "
                      f"— instrument class: ambiguous.")
    else:
        trend_line = (f"Trend: bright cells average {meas['trend_early']:.0f} per frame "
                      f"in the first half and {meas['trend_late']:.0f} in the second "
                      f"(fitted change {meas['trend_rel']:+.0%}) "
                      f"— instrument class: {meas['trend_class']}.")
    si = meas["sets_info"]
    if meas["sets"] == "none":
        sets_line = ("Set structure: no LULL marker anywhere in the stream "
                     "— the instrument reads a continuous sea, sets = none.")
    elif meas["sets"] is None:
        sets_line = (f"Set structure: {si['n_set_markers']} SET and {si['n_lull_markers']} "
                     f"LULL markers, but no complete group fits the window "
                     f"— instrument cannot call the set size.")
    else:
        sets_line = (f"Set structure: {si['n_set_markers']} SET and {si['n_lull_markers']} "
                     f"LULL markers; a complete group measures {meas['sets']} waves "
                     f"(method: {si['method']}).")
    return (
        "INSTRUMENT BRIEF — one wave stream, 55 s over a 300 m patch.\n"
        f"Dominant-train direction of travel: {meas['direction']} "
        f"(spectral peak share {meas['dir_peak_frac']:.3f}; higher means one "
        f"clean dominant train, lower means competing trains).\n"
        f"{period_line}\n"
        f"{trend_line}\n"
        f"{sets_line}"
    )

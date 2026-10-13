#!/usr/bin/env python3
"""Authoring tools for the v2 tuning run.

The teacher's worked solutions for few-shot examples are MEASURED from
the generated frames, never hand-waved: buoy-peak intervals (period),
pattern cross-correlation (direction), bright-cell density drift
(trend), and SET/LULL run lengths (sets). A candidate example sea is
only admitted to the pool if every measured estimate agrees with the
sea's ground truth inside the test's own scoring tolerance — so no
worked example ever states an observation that contradicts its label.

The model under test never runs these estimators; it imitates the
*procedure in words* (track a crest band, count the centre-cell peaks,
compare bright-cell counts early vs late, count the SET runs).
"""
import numpy as np
from sea import Sea, sample_stream, COMPASS, COMPASS_VEC
from render import assemble_stream, letter_index, markers

DT = 1.25


def buoy_peaks(times, frames):
    """Centre-cell height series -> (peak_times, est_period_s).
    Light smoothing, local maxima above a modest threshold, min gap
    3 frames (periods here are >= 6 s = 4.8 frames)."""
    n = frames.shape[1]
    c = n // 2
    s = frames[:, c, c].astype(float)
    k = np.ones(3) / 3.0
    sm = np.convolve(s, k, mode="same")
    thr = sm.mean() + 0.25 * sm.std()
    peaks = []
    for i in range(1, len(sm) - 1):
        if sm[i] >= sm[i - 1] and sm[i] > sm[i + 1] and sm[i] > thr:
            if peaks and i - peaks[-1] < 3:
                if sm[i] > sm[peaks[-1]]:
                    peaks[-1] = i
                continue
            peaks.append(i)
    if len(peaks) < 3:
        return [float(times[i]) for i in peaks], None
    ivals = np.diff([times[i] for i in peaks])
    return [float(times[i]) for i in peaks], float(np.median(ivals))


def fft_direction(frames, dt=DT):
    """Direction of travel of the dominant train, by spectral analysis
    (teacher-side tooling): average the windowed power spectrum over
    frames, take the peak in the swell annulus (wavelength 48–170 m)
    for the wavevector axis, then resolve the sign from the phase
    rate at that bin — for h = sin(k.x - wt) the +k coefficient's
    phase falls at rate w, its conjugate's rises.
    Returns (compass, (d_east_m, d_north_m) over 2.5 s, peak_power_frac)."""
    n = frames.shape[1]
    cell_m = 300.0 / (n - 1)
    win = np.outer(np.hanning(n), np.hanning(n))
    use = frames[4:21]
    specs = [np.fft.fft2(f * win, s=(128, 128)) for f in use]
    power = np.mean([np.abs(s) ** 2 for s in specs], axis=0)
    fr = np.fft.fftfreq(128, d=cell_m)          # cycles/m, both axes
    KX, KY = np.meshgrid(fr, -fr)                # row axis runs south -> ky = -fftfreq
    K = np.hypot(KX, KY)
    annulus = (K >= 1 / 170.0) & (K <= 1 / 48.0)
    P = np.where(annulus, power, 0.0)
    jr, jc = np.unravel_index(np.argmax(P), P.shape)
    # power-weighted centroid around the peak for sub-bin accuracy
    sub = P[max(0, jr - 2):jr + 3, max(0, jc - 2):jc + 3]
    rr, cc = np.mgrid[max(0, jr - 2):jr + 3, max(0, jc - 2):jc + 3]
    kx = float((sub * KX[max(0, jr - 2):jr + 3, max(0, jc - 2):jc + 3]).sum() / sub.sum())
    ky = float((sub * KY[max(0, jr - 2):jr + 3, max(0, jc - 2):jc + 3]).sum() / sub.sum())
    # phase rate at the peak bin across frames
    vals = np.array([s[jr, jc] for s in specs])
    ph = np.unwrap(np.angle(vals))
    tt = np.arange(len(vals)) * dt
    rate = float(np.polyfit(tt, ph, 1)[0])
    if rate > 0:      # picked the conjugate bin: travel is along -k
        kx, ky = -kx, -ky
    lam = 1.0 / max(np.hypot(kx, ky), 1e-9)
    dots = {k: kx * v[0] + ky * v[1] for k, v in COMPASS_VEC.items()}
    snap = max(dots, key=dots.get)
    frac = float(P[jr, jc] / power[annulus].sum()) if power[annulus].sum() > 0 else 0.0
    # displacement the work-through quotes: celerity x 2.5 s along travel
    return snap, (kx, ky, lam), frac


def trend_measure(frames):
    """Trend from the bright-cell density series (letter index >= 6,
    i.e. '*','#','%','@') over ALL frames: a least-squares slope plus
    a first-half/second-half comparison. Short windows are useless —
    the set envelope (period up to ~50 s) swamps them; the two
    statistics must agree on the class.
    Returns (early_mean, late_mean, rel_change, klass) where
    rel_change is the fitted total relative change across the stream
    and early/late are half-stream mean bright counts per frame."""
    idx = np.stack([letter_index(f) for f in frames])
    bright = (idx >= 6).sum(axis=(1, 2)).astype(float)
    half = len(bright) // 2
    e = float(bright[:half].mean())
    l = float(bright[half:].mean())
    x = np.arange(len(bright))
    slope = float(np.polyfit(x, bright, 1)[0]) if bright.mean() > 0 else 0.0
    rel = slope * len(bright) / bright.mean() if bright.mean() > 0 else 0.0
    def klass_of(v, hi, lo):
        return "building" if v > hi else ("easing" if v < lo else "steady")
    k_slope = klass_of(rel, 0.30, -0.30)
    ratio = l / e if e > 0 else 9.9
    k_half = klass_of(ratio - 1.0, 0.25, -0.22)
    # class comes from the slope; the halves statistic only vetoes on
    # a STRONG contradiction (envelope phase can bias a half either way)
    klass = k_slope
    if k_slope == "building" and ratio < 0.69:
        klass = "ambiguous"
    elif k_slope == "easing" and ratio > 1.45:
        klass = "ambiguous"
    elif k_slope == "steady" and (ratio > 1.45 or ratio < 0.69):
        klass = "ambiguous"
    return e, l, rel, klass


def sets_measure(times, frames, period_s, sets, phase0):
    """Waves-per-set from the rendered marker structure. Window edges
    truncate groups, so raw in-set runs are fragments. Two honest
    routes, in preference order:
      'run'   — a COMPLETE set: an in-set run bounded by LULLs on both
                sides (or by a LULL and a SET-transition structure);
                waves = run_frames x dt / period.
      'cycle' — >=2 SET markers: cycle = median SET-to-SET span,
                lull = median LULL-to-next-SET span;
                waves = (cycle - lull) / period.
    Returns (est_or_'none', info dict) — est None if neither route
    can see a whole group (the example is then dropped)."""
    marks = markers(times, period_s, sets, phase0)
    info = {"n_set_markers": marks.count("SET"), "n_lull_markers": marks.count("LULL"),
            "method": None, "run_frames": None, "cycle_s": None, "lull_s": None}
    if info["n_lull_markers"] == 0:
        info["method"] = "none"
        return "none", info
    # reconstruct the per-frame in-set boolean from the markers
    state = marks[0] == "SET"
    inset = []
    for m in marks:
        if m == "SET":
            state = True
        elif m == "LULL":
            state = False
        inset.append(state)
    # runs of True/False with edge flags
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
        return int(round(med * DT / period_s)), info
    set_starts = [s for v, s, e, tl, tr_ in runs if v and not tl]
    if len(set_starts) >= 2 and complete_lulls:
        cycle = float(np.median(np.diff(set_starts))) * DT
        lull = float(np.median(complete_lulls)) * DT
        info.update(method="cycle", cycle_s=cycle, lull_s=lull)
        return int(round((cycle - lull) / period_s)), info
    return None, info


def author_example(sea, times, frames):
    """Measure everything; return (ok, workthrough_text, measured) —
    ok only when every estimate agrees with truth within tolerance."""
    tr = sea.truth()
    meas = {}
    ok = True
    # period
    pk_t, est_T = buoy_peaks(times, frames)
    meas["peak_times"] = [round(t, 1) for t in pk_t]
    meas["est_period"] = None if est_T is None else round(est_T, 2)
    if est_T is None or abs(est_T - sea.period_s) > max(1.0, 0.15 * sea.period_s):
        ok = False
    # direction
    snap, (kx, ky, lam), pfrac = fft_direction(frames)
    meas["fft_dir"] = snap
    meas["fft_lambda_m"] = round(lam)
    meas["fft_peak_frac"] = round(pfrac, 3)
    if snap != sea.direction:
        ok = False
    # trend
    e, l, rel, klass = trend_measure(frames)
    meas["bright_early_half"] = round(e, 1)
    meas["bright_late_half"] = round(l, 1)
    meas["trend_rel_change"] = round(rel, 2)
    meas["trend_class"] = klass
    if klass != sea.trend:
        ok = False
    # sets
    est_sets, sinfo = sets_measure(times, frames, sea.period_s, sea.sets, sea.env_phase0)
    meas["est_sets"] = est_sets
    meas["sets_info"] = sinfo
    if est_sets != tr["sets"]:
        ok = False
    meas["ok"] = ok
    if not ok:
        return False, None, meas

    cell = 300.0 / (frames.shape[1] - 1)
    # displacement the pattern makes in 2.5 s, from the measured
    # wavelength and period, resolved along the measured direction
    disp_m = (lam / est_T) * 2.5
    ux, uy = COMPASS_VEC[sea.direction]
    de_c, dn_c = disp_m * ux / cell, disp_m * uy / cell
    pk_str = ", ".join(f"{t:.0f}" for t in pk_t[:6])
    if sea.sets is None:
        sets_txt = (f"Sets — the stream's only SET marker is at the very top and there is "
                    f"no LULL marker anywhere: the sea never breaks into groups, so sets = none.")
    elif sinfo["method"] == "run":
        runf = sinfo["run_frames"]
        sets_txt = (f"Sets — counting a complete set, from one LULL to the next: it runs about "
                    f"{runf:.0f} frames ({runf * DT:.0f} s), and at one wave every {est_T:.0f} s "
                    f"that is about {est_sets} waves per set.")
    else:
        sets_txt = (f"Sets — SET markers come every {sinfo['cycle_s']:.0f} s or so, and the LULL "
                    f"between a set and the next SET lasts about {sinfo['lull_s']:.0f} s: "
                    f"({sinfo['cycle_s']:.0f} - {sinfo['lull_s']:.0f}) / {est_T:.0f} = about "
                    f"{est_sets} waves per set.")
    wt = (
        f"Work-through: Direction — tracking the bright crest bands between two frames "
        f"2.5 s apart, the whole pattern has shifted about {abs(de_c):.0f} cells "
        f"{'east' if de_c > 0.3 else 'west' if de_c < -0.3 else ''}"
        f"{' and ' if abs(de_c) > 0.3 and abs(dn_c) > 0.3 else ''}"
        f"{abs(dn_c):.0f} cells {'north' if dn_c > 0.3 else 'south' if dn_c < -0.3 else ''}: "
        f"the train is travelling {sea.direction}. "
        f"Period — at the centre cell the brightness peaks at t = {pk_str} s: the gaps are "
        f"about {est_T:.0f} s, so the period is {est_T:.0f} s. "
        f"Trend — bright cells (letters * and brighter) average {e:.0f} per frame in the "
        f"first half of the stream and {l:.0f} in the second half: the sea is {sea.trend}. "
        f"{sets_txt}"
    )
    return True, wt, meas


def build_pool(n_candidates=40, seed=777, want=10):
    """Generate candidate example seas (shorter streams, 40 s), author
    work-throughs, keep the ones whose measurements all agree."""
    rng = np.random.default_rng(seed)
    pool = []
    tries = 0
    while len(pool) < want and tries < n_candidates:
        tries += 1
        direction = COMPASS[tries % 8]
        trend = ["building", "easing", "steady"][tries % 3]
        sets = [3, 4, 5, None][tries % 4]
        period = float([6.0, 7.0, 8.0][tries % 3])
        sea = Sea(rng, direction=direction, period_s=period, trend=trend, sets=sets)
        times, frames = sample_stream(sea, duration=40.0, n=20)
        ok, wt, meas = author_example(sea, times, frames)
        print(f"  cand {tries:2d} dir={sea.direction:2s} T={sea.period_s:.0f} trend={sea.trend:8s} "
              f"sets={str(sea.sets):4s} -> {'KEEP' if ok else 'drop'} {'' if ok else meas}")
        if ok:
            pool.append({"sea": sea, "times": times, "frames": frames,
                         "workthrough": wt, "measured": meas})
    return pool


if __name__ == "__main__":
    pool = build_pool()
    print(f"\npool: {len(pool)} verified examples")
    for i, p in enumerate(pool):
        s = p["sea"]
        print(f"  [{i}] dir={s.direction} T={s.period_s:.0f} trend={s.trend} sets={s.sets} phase0={s.env_phase0:.1f}")

#!/usr/bin/env python3
"""Route A v4 — envelope-aware measurement (2026-10-13).

v3's settlement left two open measurement problems, both diagnosed in
RESULTS.md as the same underlying fight: the SET ENVELOPE swamps the
statistics that were supposed to measure something else.

  trend 0.67 — the bright-cell slope statistic reads the envelope's
  within-window trajectory as trend; misses bleed to the adjacent
  class. Fix here: measure the envelope's trajectory explicitly and
  divide it out. Per-wave crest amplitudes are regressed as
      log A_k = a + b*u_k + c*log E_hat(phi_k)
  where E_hat is the expected set-envelope value at wave k's
  reconstructed position in its group cycle. The class comes from b
  alone — the fitted trend with the envelope held as a covariate,
  not from raw height change.

  sets 0.75 = 27/27 when callable + 9 honest unknowns — the v3
  estimator declined whenever no complete set fit the 55 s window.
  Fix here: two further routes before declining.
    (a) spacing+prior: set-start to set-start spacing is a complete
        group cycle even when every set and lull inside it is
        edge-truncated; combined with the family lull constant
        (lull duration = 1.4 wave periods, sea.set_envelope) it
        pins N. Cross-checked against any complete lull.
    (b) envelope matched filter: the observed per-frame amplitude
        envelope (detrended) is correlated against the generator
        family's envelope shapes over (N, phase0) hypotheses; the
        phase the window opened at is searched, not assumed.
  "Unknown" survives only when the routes that can speak conflict
  or none can speak — the honest-unknown class is kept on purpose.

Direction and period are NOT re-implemented: they are imported from
the same estimators v3 used (FFT direction, buoy peaks), so the v4
run doubles as their regression check on a fresh seed.

Calibration disclosure: two constants come from the sea family
itself — the lull length 1.4 periods and the envelope shape in
sea.set_envelope. A deployed instrument is calibrated to its sensor
family the same way; both are stated here rather than hidden.
Classification thresholds are set a priori from the generator's
ramp geometry (building/easing ramps run 0.62 -> 1.38, a log ratio
of ~0.80; the steady wobble is +-4%), not fitted to the test set.
"""
import numpy as np
from authoring import buoy_peaks, fft_direction, trend_measure
from prereader import parse_markers, sets_estimate
from render import assemble_stream
from sea import set_envelope

DT = 1.25
LULL_PERIODS = 1.4          # family constant: lull duration in wave periods
TREND_LOG_SLOPE = 0.25      # |b| above this = building/easing (true ramps ~0.80)
TREND_RESID_MAX = 0.35      # log-space residual std above this = ambiguous
MIN_WAVES = 5
FILTER_RMSE_MAX = 0.20      # normalized-envelope RMSE to accept a filter call
FILTER_MARGIN = 0.85        # best N must beat runner-up N by this factor


# ---------------------------------------------------------------- waves

def wave_amplitudes(times, frames, est_T, peak_times):
    """Per-wave crest amplitudes on a uniform wave grid.

    The grid is anchored on the first buoy peak and steps by the
    estimated period, so a peak the centre cell misses inside a deep
    lull does not break the segmentation. Amplitude per wave is the
    robust crest-to-trough half-range of the pooled field over the
    wave's frames: (p98 - p2) / 2.
    Returns (mids, amps, u) — wave mid-times, amplitudes, and each
    mid's fraction through the window — or None if not enough waves.
    """
    if est_T is None or est_T <= 0:
        return None
    t0, t1 = float(times[0]), float(times[-1])
    anchor = float(peak_times[0]) if peak_times else t0
    starts = []
    s = anchor
    while s - est_T >= t0 - 1e-9:      # extend the grid back to t0
        s -= est_T
    while s < t1:
        starts.append(s)
        s += est_T
    mids, amps = [], []
    times = np.asarray(times, dtype=float)
    for s in starts:
        sel = (times >= s) & (times < s + est_T)
        if sel.sum() < 2:
            continue
        pool = frames[sel].ravel()
        amps.append((np.percentile(pool, 98) - np.percentile(pool, 2)) / 2.0)
        mids.append(s + est_T / 2.0)
    if len(amps) < MIN_WAVES:
        return None
    mids = np.array(mids)
    u = (mids - t0) / max(t1 - t0, 1e-9)
    return mids, np.array(amps), u


# ---------------------------------------------------------------- envelope

def inset_series(marks):
    """Per-frame in-set boolean reconstructed from the marker channel
    (same reconstruction the v3 estimator uses)."""
    state = marks[0] == "SET"
    inset = []
    for m in marks:
        if m == "SET":
            state = True
        elif m == "LULL":
            state = False
        inset.append(state)
    return inset


def envelope_runs(marks):
    """Runs of the in-set boolean with edge flags, plus the interior
    set-start frame indices (LULL->SET transitions, frame > 0)."""
    inset = inset_series(marks)
    runs = []
    s0 = 0
    for i in range(1, len(inset) + 1):
        if i == len(inset) or inset[i] != inset[s0]:
            runs.append((inset[s0], s0, i, s0 == 0, i == len(inset)))
            s0 = i
    starts = [s for v, s, e, tl, tr_ in runs if v and not tl]
    return inset, runs, starts


def expected_envelope(tau, starts_t, group_period, n_sets):
    """The family envelope shape at time tau, given the observed
    set-start times and group period. Phase is reconstructed from
    the nearest cycle origin; outside the observed starts the grid
    is extrapolated by whole group periods."""
    if n_sets is None or group_period is None or group_period <= 0:
        return None
    if len(starts_t):
        starts_t = np.sort(np.asarray(starts_t, dtype=float))
        j = np.searchsorted(starts_t, tau, side="right") - 1
        if j >= 0:
            origin = starts_t[j]
        else:
            origin = starts_t[0] - group_period * np.ceil((starts_t[0] - tau) / group_period)
    else:
        origin = 0.0
    phi = ((tau - origin) % group_period) / group_period
    on_frac = n_sets / (n_sets + LULL_PERIODS)
    if phi < on_frac:
        return 0.30 + 0.70 * np.sin(np.pi * phi / on_frac) ** 1.5
    return 0.30


def dominant_envelope(frames, kx, ky):
    """Per-frame amplitude of the DOMINANT train alone: project each
    frame onto the measured dominant wavevector and take the
    coefficient's magnitude. The percentile half-range of the whole
    field mixes in the secondary train, whose beat against the
    dominant modulates the raw amplitude with a rhythm that is not
    the set envelope; the projection isolates the train the envelope
    actually modulates. (kx, ky) are cycles/m in (east, north), the
    fft_direction convention; the grid is sea.sample_stream's."""
    n = frames.shape[1]
    xs = np.linspace(-150.0, 150.0, n)
    ys = np.linspace(150.0, -150.0, n)          # row 0 = north
    X, Y = np.meshgrid(xs, ys)
    basis = np.exp(-2j * np.pi * (kx * X + ky * Y))
    coef = np.tensordot(frames, basis, axes=((1, 2), (0, 1))) / (n * n)
    return np.abs(coef)


# ---------------------------------------------------------------- trend v4

def trend_measure_v4(times, frames, est_T, peak_times, marks, est_sets):
    """Envelope-aware trend. Returns (klass, diag): klass in
    building/easing/steady/ambiguous (ambiguous = the instrument
    declining, scored wrong like v3's dead zones)."""
    diag = {"method": None}
    wav = wave_amplitudes(times, frames, est_T, peak_times)
    if wav is None:
        e, l, rel, klass = trend_measure(frames)
        diag.update(method="v3-fallback", rel=round(float(rel), 3))
        return klass, diag
    mids, amps, u = wav
    logA = np.log(np.maximum(amps, 1e-6))

    # expected envelope at each wave
    inset, runs, starts = envelope_runs(marks)
    starts_t = [float(times[s]) for s in starts]
    group_period = None
    if len(starts_t) >= 2:
        group_period = float(np.median(np.diff(starts_t)))
    elif isinstance(est_sets, int) and est_T:
        group_period = (est_sets + LULL_PERIODS) * est_T
    logE = None
    if isinstance(est_sets, int) and group_period:
        ev = [expected_envelope(m, starts_t, group_period, est_sets) for m in mids]
        if all(v is not None and v > 0 for v in ev):
            logE = np.log(np.array(ev))

    X = [np.ones_like(u), u]
    if logE is not None and np.std(logE) > 0.05:
        X.append(logE)
    X = np.column_stack(X)
    beta, *_ = np.linalg.lstsq(X, logA, rcond=None)
    resid = logA - X @ beta
    b = float(beta[1])
    diag.update(method="envelope-regression" if X.shape[1] == 3 else "slope-only",
                slope_b=round(b, 3), resid_std=round(float(resid.std()), 3),
                n_waves=len(amps),
                env_coef=None if X.shape[1] < 3 else round(float(beta[2]), 3))
    if float(resid.std()) > TREND_RESID_MAX:
        return "ambiguous", diag
    if b > TREND_LOG_SLOPE:
        return "building", diag
    if b < -TREND_LOG_SLOPE:
        return "easing", diag
    return "steady", diag


# ---------------------------------------------------------------- sets v4

def sets_estimate_v4(marks, est_T, times, frames, detrend_b=0.0, env_obs=None):
    """Waves-per-set with truncated-window routes. Returns (est, info)
    with est an int, "none", or None (honest unknown)."""
    info = {"n_set_markers": marks.count("SET"),
            "n_lull_markers": marks.count("LULL"), "method": None}
    if info["n_lull_markers"] == 0:
        info["method"] = "none"
        return "none", info
    if est_T is None:
        info["method"] = "no-period"
        return None, info

    # stage 1: the v3 routes, untouched (27/27 when callable in v3)
    est, sinfo = sets_estimate(marks, est_T)
    if est is not None:
        info.update(method="v3-" + str(sinfo.get("method")), v3_info=sinfo)
        return est, info

    inset, runs, starts = envelope_runs(marks)
    complete_lulls = [(e - s) * DT for v, s, e, tl, tr_ in runs
                      if not v and not tl and not tr_]
    set_frag_max = max([(e - s) * DT for v, s, e, tl, tr_ in runs if v] or [0.0])

    # stage 2: set-start spacing + the family lull constant
    if len(starts) >= 2:
        starts_t = np.array([float(times[s]) for s in starts])
        G = float(np.median(np.diff(starts_t)))
        n_a = int(round(G / est_T - LULL_PERIODS))
        ok = 2 <= n_a <= 6 and set_frag_max <= n_a * est_T + DT
        n_b = None
        if complete_lulls:
            L = float(np.median(complete_lulls))
            n_b = int(round((G - L) / est_T))
            ok = ok and (n_b == n_a) and abs(L - LULL_PERIODS * est_T) < 0.75 * est_T
        if ok:
            info.update(method="spacing+prior", group_s=round(G, 1),
                        n_spacing=n_a, n_lull=n_b)
            return n_a, info
        info.update(spacing_rejected={"group_s": round(G, 1), "n_a": n_a, "n_b": n_b})

    # stage 3: envelope matched filter over (N, phase0). Observed
    # envelope: the dominant-train projection when the caller
    # supplies it, else the whole-field percentile half-range.
    if env_obs is None:
        env_obs = np.array([(np.percentile(f, 98) - np.percentile(f, 2)) / 2.0
                            for f in frames])
    tt = np.asarray(times, dtype=float)
    u_t = (tt - tt[0]) / max(tt[-1] - tt[0], 1e-9)
    env_detr = env_obs / np.exp(detrend_b * u_t)
    env_detr = env_detr / max(env_detr.mean(), 1e-9)
    smooth = np.convolve(env_detr, np.ones(3) / 3.0, mode="same")
    best = {}
    for N in (3, 4, 5):
        G = (N + LULL_PERIODS) * est_T
        steps = max(8, int(round(G / (est_T / 8.0))))
        rmses = []
        for j in range(steps):
            ph0 = j * G / steps
            pred = np.array([set_envelope(float(t), est_T, N, ph0) for t in tt])
            pred = pred / max(pred.mean(), 1e-9)
            rmses.append(float(np.sqrt(np.mean((smooth - pred) ** 2))))
        best[N] = min(rmses)
    ranked = sorted(best.items(), key=lambda kv: kv[1])
    (n_best, r_best), (_, r_second) = ranked[0], ranked[1]
    info.update(filter_rmse={str(k): round(v, 3) for k, v in best.items()})
    if r_best < FILTER_RMSE_MAX and r_best < FILTER_MARGIN * r_second:
        # consistency: no observed set fragment may exceed the fit
        if set_frag_max <= n_best * est_T + DT:
            info.update(method="envelope-filter")
            return n_best, info
        info["filter_rejected"] = "fragment longer than fitted set"
    info["method"] = "truncated"
    return None, info


# ---------------------------------------------------------------- measure

def measure_v4(times, frames, sea):
    """Run every v4 estimator. Same measurement contract as
    prereader.measure (rendered marker channel + height field);
    direction/period come from the identical v3 estimators."""
    stream_text = assemble_stream(times, frames, sea.period_s, sea.sets,
                                  "letters", phase0=sea.env_phase0)
    marks = parse_markers(stream_text)
    pk_t, est_T = buoy_peaks(times, frames)
    snap, (kx, ky, lam), frac = fft_direction(frames)

    # preliminary detrending slope for the sets matched filter:
    # plain log-linear fit of the per-wave amplitudes
    detrend_b = 0.0
    wav = wave_amplitudes(times, frames, est_T, pk_t)
    if wav is not None:
        _, amps0, u0 = wav
        detrend_b = float(np.polyfit(u0, np.log(np.maximum(amps0, 1e-6)), 1)[0])

    est_sets, sinfo = sets_estimate_v4(marks, est_T, times, frames,
                                       detrend_b=detrend_b,
                                       env_obs=dominant_envelope(frames, kx, ky))
    klass, tdiag = trend_measure_v4(times, frames, est_T, pk_t, marks, est_sets)
    return {
        "direction": snap, "dir_peak_frac": round(float(frac), 3),
        "dir_lambda_m": round(float(lam)),
        "period_s": None if est_T is None else round(float(est_T), 2),
        "n_peaks": len(pk_t),
        "trend_class": klass, "trend_diag": tdiag,
        "sets": est_sets, "sets_info": sinfo,
    }


def estimator_answer_v4(meas):
    return {"direction": meas["direction"], "period_s": meas["period_s"],
            "trend": meas["trend_class"], "sets": meas["sets"]}

#!/usr/bin/env python3
"""Sea generator — procedural synthetic wave fields with exact ground truth.

A sea is a superposition of:
  - a DOMINANT swell train (the one the reading test asks about),
  - a secondary swell train (weaker, different direction),
  - short wind chop (2-3 small components),
all modulated by:
  - a SET envelope (groups of N big waves separated by lulls), and
  - a slow TREND ramp (building / easing / steady overall amplitude).

The field is sampled on a square patch (PATCH_M metres across) as a time
series of 2D height grids. Every parameter that the reading test asks
about is recorded in the returned `truth` dict — the answers are exact
by construction, no estimation anywhere.

Coordinates: x = east, y = north. Grid row 0 is the NORTH edge of the
patch (so grids print like a map). Direction is the direction the
dominant swell TRAVELS TOWARD, as an 8-point compass label.

Physics: deep-water dispersion, wavelength = g*T^2/(2*pi) ~= 1.56*T^2 m.

GENERATOR v2 (2026-10-13): the set envelope's starting phase is
randomized per sea (Sea.env_phase0). v1 always opened every stream at
phase 0 — the start of a set — a confound flagged in RESULTS.md.
Pass env_phase0=0.0 to reproduce v1 streams exactly (the phase draw is
the LAST rng draw in __init__, so all other attributes keep their v1
draw order either way).
"""
import numpy as np

G = 9.81
GENERATOR_VERSION = "2"
COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
# unit vectors (east, north) for direction of travel
COMPASS_VEC = {
    "N": (0.0, 1.0), "NE": (0.7071, 0.7071), "E": (1.0, 0.0),
    "SE": (0.7071, -0.7071), "S": (0.0, -1.0), "SW": (-0.7071, -0.7071),
    "W": (-1.0, 0.0), "NW": (-0.7071, 0.7071),
}
PATCH_M = 300.0  # patch width in metres


def wavelength(period_s):
    return G * period_s ** 2 / (2.0 * np.pi)


def set_envelope(t, period_s, sets, phase0=0.0):
    """Amplitude envelope in [lull_floor, 1] from set grouping.

    sets: int N (groups of N waves, then a lull of ~1.4 wave periods)
          or None (continuous sea, envelope ~1 with mild breathing).
    Implemented as a smooth raised-cosine gate so crests grow and die
    gradually, like real wave groups.
    phase0: seconds offset into the group cycle at t=0 (v2; v1 was
    always 0, so every stream opened at the start of a set).
    """
    if sets is None:
        return 0.92 + 0.08 * np.sin(2 * np.pi * t / (7.3 * period_s))
    group_period = (sets + 1.4) * period_s
    phase = ((t + phase0) % group_period) / group_period  # 0..1 within a group cycle
    on_frac = sets / (sets + 1.4)              # fraction of cycle "in the set"
    if phase < on_frac:
        # inside the set: smooth hump, 0.30 at the edges, 1.0 mid-set
        return 0.30 + 0.70 * np.sin(np.pi * phase / on_frac) ** 1.5
    # in the lull: low, with a faint ripple
    return 0.30 + 0.06 * np.sin(2 * np.pi * t / period_s)


def trend_ramp(t, duration, trend):
    """Slow overall-amplitude multiplier."""
    u = t / duration
    if trend == "building":
        return 0.62 + 0.76 * u      # 0.62 -> 1.38
    if trend == "easing":
        return 1.38 - 0.76 * u      # 1.38 -> 0.62
    return 1.0 + 0.04 * np.sin(2 * np.pi * u)  # steady


class Sea:
    def __init__(self, rng, direction=None, period_s=None, trend=None, sets="random",
                 env_phase0=None):
        self.direction = direction or COMPASS[rng.integers(0, 8)]
        self.period_s = float(period_s) if period_s else float(rng.choice([6.0, 7.0, 8.0, 9.0, 10.0]))
        self.trend = trend or ["building", "easing", "steady"][rng.integers(0, 3)]
        if sets == "random":
            sets = [3, 4, 5, None][rng.integers(0, 4)]
        self.sets = sets  # int or None
        # dominant train
        self.amp_dom = float(rng.uniform(0.85, 1.25))
        # secondary train: 30-50% amplitude, >=45 deg away, different period
        off = int(rng.choice([1, 2, 3, 5, 6, 7]))  # compass steps away
        self.dir_sec = COMPASS[(COMPASS.index(self.direction) + off) % 8]
        self.period_sec = float(np.clip(self.period_s * rng.uniform(0.7, 1.45), 4.5, 13.0))
        self.amp_sec = self.amp_dom * float(rng.uniform(0.30, 0.50))
        self.phase_sec = float(rng.uniform(0, 2 * np.pi))
        self.phase_dom = float(rng.uniform(0, 2 * np.pi))
        # wind chop: 3 short components
        self.chop = []
        for _ in range(3):
            lam = float(rng.uniform(14.0, 30.0))
            ang = float(rng.uniform(0, 2 * np.pi))
            self.chop.append({
                "lam": lam,
                "kx": 2 * np.pi / lam * np.cos(ang),
                "ky": 2 * np.pi / lam * np.sin(ang),
                "omega": np.sqrt(G * 2 * np.pi / lam),
                "amp": float(rng.uniform(0.08, 0.20)),
                "phase": float(rng.uniform(0, 2 * np.pi)),
            })
        # v2: where in the set cycle does the stream open? Drawn LAST,
        # after every v1 attribute, so v1 rng draw order is preserved;
        # pass env_phase0=0.0 explicitly to reproduce v1 exactly.
        if env_phase0 is None:
            if self.sets is not None:
                env_phase0 = float(rng.uniform(0, (self.sets + 1.4) * self.period_s))
            else:
                env_phase0 = 0.0
        self.env_phase0 = float(env_phase0)
        self.rng = rng

    def truth(self):
        return {
            "direction": self.direction,
            "period_s": self.period_s,
            "trend": self.trend,
            "sets": self.sets if self.sets is not None else "none",
            "amp_dom_m": round(self.amp_dom, 2),
            "env_phase0_s": round(self.env_phase0, 2),
            "generator": GENERATOR_VERSION,
            "secondary": {"direction": self.dir_sec, "period_s": round(self.period_sec, 1)},
        }

    def height(self, X, Y, t, duration):
        """Height field (m) at time t. X, Y are meshgrid arrays in metres."""
        env = set_envelope(t, self.period_s, self.sets, self.env_phase0) * trend_ramp(t, duration, self.trend)
        # dominant
        lam = wavelength(self.period_s)
        ux, uy = COMPASS_VEC[self.direction]
        k = 2 * np.pi / lam
        omega = 2 * np.pi / self.period_s
        h = self.amp_dom * np.sin(k * (ux * X + uy * Y) - omega * t + self.phase_dom)
        # secondary (envelope applies to swell family, slightly weaker)
        lam2 = wavelength(self.period_sec)
        ux2, uy2 = COMPASS_VEC[self.dir_sec]
        k2 = 2 * np.pi / lam2
        omega2 = 2 * np.pi / self.period_sec
        h = h + self.amp_sec * np.sin(k2 * (ux2 * X + uy2 * Y) - omega2 * t + self.phase_sec)
        h = h * env
        # chop (not enveloped — wind sea is always there)
        for c in self.chop:
            h = h + c["amp"] * np.sin(c["kx"] * X + c["ky"] * Y - c["omega"] * t + c["phase"])
        return h


def sample_stream(sea, duration=55.0, dt=1.25, n=20):
    """Sample a stream: returns (times, frames) with frames an array
    (n_frames, n, n) of heights in metres on an n x n grid."""
    xs = np.linspace(-PATCH_M / 2, PATCH_M / 2, n)
    ys = np.linspace(PATCH_M / 2, -PATCH_M / 2, n)  # row 0 = north
    X, Y = np.meshgrid(xs, ys)
    times = np.arange(0.0, duration + 1e-9, dt)
    frames = np.stack([sea.height(X, Y, t, duration) for t in times])
    return times, frames


def in_set(t, period_s, sets, phase0=0.0):
    """Ground-truth: is time t inside a set (vs a lull)? For stream markers."""
    if sets is None:
        return True
    group_period = (sets + 1.4) * period_s
    phase = ((t + phase0) % group_period) / group_period
    return phase < sets / (sets + 1.4)


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    sea = Sea(rng)
    times, frames = sample_stream(sea)
    print("truth:", sea.truth())
    print("frames:", frames.shape, "height range: %.2f..%.2f m" % (frames.min(), frames.max()))

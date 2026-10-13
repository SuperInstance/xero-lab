#!/usr/bin/env python3
"""Letter renderer — wave height grids -> pulsed letter streams.

Design rules (from the seed):
  - FIXED height scale for a whole stream: letters are comparable
    frame-to-frame, so a building sea literally gets brighter and an
    easing sea dimmer. (Per-frame normalization would erase the trend.)
  - The stream is PULSED: frames are grouped by the sea's own sets,
    with a ~~~ LULL ~~~ marker in the quiet water between sets —
    the lull is the break, like the pause in speech.
  - Delta mode: after a full keyframe, emit only the cells whose
    letter changed (delta-vector doctrine: encode what changed).

Ramp: 10 levels from trough (space) to crest (@), scale +-SCALE_M.
"""
import numpy as np
from sea import in_set

RAMP = " .:-=+*#%@"       # 10 levels, index 0 = deepest trough
SCALE_M = 1.8             # heights beyond +-SCALE_M clip to the end letters


def letter_index(frame):
    return np.clip(((frame + SCALE_M) / (2 * SCALE_M) * len(RAMP)).astype(int),
                   0, len(RAMP) - 1)


def to_letters(frame):
    """One height grid -> list of strings (rows, north first)."""
    idx = letter_index(frame)
    return ["".join(RAMP[i] for i in row) for row in idx]


def to_numeric(frame):
    """One height grid -> list of strings, 1-decimal metres."""
    return [" ".join(f"{v:+.1f}" for v in row) for row in frame]


def markers(times, period_s, sets, phase0=0.0):
    """Per-frame structural marker: 'SET' when a set begins, 'LULL' when
    a lull begins, else None. Frame 0 gets 'SET' if it starts in a set.
    phase0 (generator v2): the sea's set-envelope starting phase."""
    out = []
    prev = None
    for t in times:
        cur = in_set(float(t), period_s, sets, phase0)
        if prev is None:
            out.append("SET" if cur else None)
        elif cur and not prev:
            out.append("SET")
        elif prev and not cur:
            out.append("LULL")
        else:
            out.append(None)
        prev = cur
    return out


def assemble_stream(times, frames, period_s, sets, fmt="letters", phase0=0.0):
    """Full pulsed stream text. fmt: 'letters' or 'numeric'.
    Structural markers are identical across formats (held constant so
    the reading test compares encodings, not stream structure)."""
    marks = markers(times, period_s, sets, phase0)
    lines = []
    for i, (t, fr) in enumerate(zip(times, frames)):
        if marks[i] == "SET":
            lines.append("--- SET ---")
        elif marks[i] == "LULL":
            lines.append("~~~ LULL ~~~")
        lines.append(f"[t={t:.1f}s]")
        lines.extend(to_letters(fr) if fmt == "letters" else to_numeric(fr))
    return "\n".join(lines)


def summary_stream(times, frames, period_s=None, sets=None, phase0=0.0):
    """Control (c): per-frame statistics + a centre 'buoy' time series.
    This is what classical instruments give: exact numbers, no picture.
    A single point cannot see direction; the frame stats cannot either.
    SET/LULL markers are included when period/sets are given, holding
    stream structure constant across encodings."""
    n = frames.shape[1]
    c = n // 2
    marks = markers(times, period_s, sets, phase0) if period_s is not None else [None] * len(times)
    lines = []
    for i, (t, fr) in enumerate(zip(times, frames)):
        if marks[i] == "SET":
            lines.append("--- SET ---")
        elif marks[i] == "LULL":
            lines.append("~~~ LULL ~~~")
        lines.append(
            f"t={t:5.1f}s mean={fr.mean():+.2f} std={fr.std():.2f} "
            f"max={fr.max():+.2f} min={fr.min():+.2f} buoy={fr[c, c]:+.2f}")
    return "\n".join(lines)


def delta_encode(letter_frames):
    """Delta-encode a sequence of letter frames (list of list-of-str).
    Returns the encoded text. Frame 0 is a full keyframe; later frames
    list only changed cells as r<row>c<col><char> tokens."""
    out = []
    prev = None
    for i, fr in enumerate(letter_frames):
        if prev is None:
            out.append(f"#{i} KEY")
            out.extend(fr)
        else:
            changes = []
            for r, (row_new, row_old) in enumerate(zip(fr, prev)):
                for cidx, (a, b) in enumerate(zip(row_new, row_old)):
                    if a != b:
                        changes.append(f"r{r}c{cidx}{a}")
            if changes:
                out.append(f"#{i} " + " ".join(changes))
            else:
                out.append(f"#{i} =")
        prev = fr
    return "\n".join(out)


def changed_fraction(letter_frames):
    """Mean fraction of cells whose letter changes between frames."""
    fr = letter_frames
    fracs = []
    for a, b in zip(fr[:-1], fr[1:]):
        diff = sum(1 for ra, rb in zip(a, b) for x, y in zip(ra, rb) if x != y)
        fracs.append(diff / (len(a) * len(a[0])))
    return float(np.mean(fracs)) if fracs else 0.0


def deadband_delta_encode(frames, deadband=2):
    """Delta with a DEADBAND: a cell is re-emitted only when its letter
    index has moved at least `deadband` levels from the last EMITTED
    value (not from last frame's value). Sub-deadband flicker — chop,
    quantisation shimmer — is never written. This is the gate doctrine
    applied to logging: change must be this big to count as change.
    Returns (text, stats). The decoder state is the emitted grid."""
    idx_frames = [letter_index(f) for f in frames]
    out = []
    emitted = None
    total_changes = 0
    cells = idx_frames[0].size
    for i, idx in enumerate(idx_frames):
        if emitted is None:
            out.append(f"#{i} KEY")
            out.extend("".join(RAMP[v] for v in row) for row in idx)
            emitted = idx.copy()
            continue
        moved = np.abs(idx - emitted) >= deadband
        n = int(moved.sum())
        total_changes += n
        if n == 0:
            out.append(f"#{i} =")
        else:
            toks = []
            rows, cols = np.nonzero(moved)
            for r, c in zip(rows, cols):
                toks.append(f"r{r}c{c}{RAMP[idx[r, c]]}")
                emitted[r, c] = idx[r, c]
            out.append(f"#{i} " + " ".join(toks))
    stats = {"mean_changed_cells_per_frame": total_changes / max(1, len(frames) - 1),
             "cells_per_frame": int(cells)}
    return "\n".join(out), stats

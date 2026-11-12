"""Pure-Python logic and scoring computation for paper_tray_side_guides."""

from __future__ import annotations

import math
from typing import Mapping, Sequence

from geometry import (
    BLOCK_CENTRING_THRESHOLD_M,
    FRAME_POS_WORLD,
    GUIDE_A_NAME,
    GUIDE_B_NAME,
    GUIDE_CONTACT_THRESHOLD_M,
    MAX_FRAME_DRIFT_GATE_M,
    MAX_PAPER_TILT_RAD,
    PAPER_DIMS_M,
    TABLE_TOP,
    TRAY_CLOSED_TOLERANCE_M,
    TRAY_CLOSED_X,
    TRAY_DIMS_M,
)


def compute_drift(pos: Sequence[float], origin: Sequence[float]) -> float:
    """Euclidean distance in XY plane."""
    return math.hypot(pos[0] - origin[0], pos[1] - origin[1])


def is_paper_in_tray(
    paper_pos: Sequence[float],
    tray_pos: Sequence[float],
) -> bool:
    """Check if paper block is inside the tray outline in XY and resting at tray height."""
    # Tray interior dimensions (240x320 minus rims = 234x314 mm)
    # Paper stack dimensions: 150x210x30 mm
    # For paper to be inside tray outline:
    # distance between centres along x <= (tray_inner_x - paper_x)/2
    # max dx = (0.234 - 0.150) / 2 = 0.042 m (allow 0.046 m with 4 mm margin)
    # max dy = (0.314 - 0.210) / 2 = 0.052 m (allow 0.056 m with 4 mm margin)
    dx = abs(paper_pos[0] - tray_pos[0])
    dy = abs(paper_pos[1] - tray_pos[1])

    # Paper z: tray origin is at tray base (z = TABLE_TOP + 0.010)
    # Tray floor is 4 mm thick; paper centre is 15 mm above floor
    # expected paper_z = tray_pos[2] + 0.004 + 0.015 = tray_pos[2] + 0.019
    dz = paper_pos[2] - tray_pos[2]

    in_xy = (dx <= 0.046) and (dy <= 0.056)
    in_z = (0.005 <= dz <= 0.045)
    return in_xy and in_z


def compute_paper_tilt(quat_xyzw: Sequence[float] | None) -> float:
    """Returns tilt angle in radians from horizontal (upright Z)."""
    if quat_xyzw is None:
        return 0.0
    x, y, z, w = (float(v) for v in quat_xyzw)
    # Dot product of local Z with world Z is R[2, 2] = 1 - 2*(x^2 + y^2)
    cos_tilt = 1.0 - 2.0 * (x * x + y * y)
    cos_tilt = max(-1.0, min(1.0, cos_tilt))
    return math.acos(cos_tilt)


def compute_guide_gaps(
    tray_pos: Sequence[float],
    paper_pos: Sequence[float],
    sliders: Mapping[str, float],
) -> tuple[float, float]:
    """Calculate distance (m) between guide inner faces and the paper block sides."""
    disp_a = abs(float(sliders.get(GUIDE_A_NAME, 0.0)))
    disp_b = abs(float(sliders.get(GUIDE_B_NAME, 0.0)))

    # Guide A: starts at tray_y + 0.135, inner face at +0.130 at rest, slides inward (-Y)
    # Guide A inner face in world coordinates:
    guide_a_y = tray_pos[1] + 0.130 - disp_a
    # Paper +y face:
    paper_top_y = paper_pos[1] + PAPER_DIMS_M[1] / 2
    gap_a = abs(guide_a_y - paper_top_y)

    # Guide B: starts at tray_y - 0.135, inner face at -0.130 at rest, slides inward (+Y)
    # Guide B inner face in world coordinates:
    guide_b_y = tray_pos[1] - 0.130 + disp_b
    # Paper -y face:
    paper_bottom_y = paper_pos[1] - PAPER_DIMS_M[1] / 2
    gap_b = abs(paper_bottom_y - guide_b_y)

    return gap_a, gap_b


def evaluate_state(
    frame_pos: Sequence[float],
    tray_pos: Sequence[float],
    paper_pos: Sequence[float],
    sliders: Mapping[str, float],
    paper_quat: Sequence[float] | None = None,
    resting: bool = True,
) -> tuple[float, bool, str]:
    """Evaluate state of paper_tray_side_guides task."""
    # Gate 1: Printer frame moved > 5 mm
    drift = compute_drift(frame_pos, FRAME_POS_WORLD)
    if drift > MAX_FRAME_DRIFT_GATE_M:
        return 0.0, False, f"gate: printer frame moved {drift * 1000:.1f} mm (> 5 mm)"

    # Gate 2: Paper dropped off table
    if paper_pos[2] < (TABLE_TOP - 0.020):
        return 0.0, False, f"gate: paper block fell off table (z={paper_pos[2]:.3f} m)"

    # Check if paper is inside tray outline
    in_tray = is_paper_in_tray(paper_pos, tray_pos)
    if not in_tray:
        return 0.0, False, "initial/incomplete: paper block not inside tray outline"

    # Check paper tilt (flat condition)
    tilt = compute_paper_tilt(paper_quat)
    is_flat = tilt <= MAX_PAPER_TILT_RAD

    # Check guide gaps
    gap_a, gap_b = compute_guide_gaps(tray_pos, paper_pos, sliders)
    one_guide_near = (gap_a <= GUIDE_CONTACT_THRESHOLD_M) or (gap_b <= GUIDE_CONTACT_THRESHOLD_M)
    both_guides_near = (gap_a <= GUIDE_CONTACT_THRESHOLD_M) and (gap_b <= GUIDE_CONTACT_THRESHOLD_M)

    # Check paper block centring relative to tray midline
    centring_error = abs(paper_pos[1] - tray_pos[1])
    is_centred = centring_error <= BLOCK_CENTRING_THRESHOLD_M

    # Check tray pushed shut
    tray_closed = abs(tray_pos[0] - TRAY_CLOSED_X) <= TRAY_CLOSED_TOLERANCE_M

    # Ladder 1.0: Paper flat in tray, both guides near, centred, tray shut, resting
    if is_flat and both_guides_near and is_centred and tray_closed and resting:
        return 1.0, True, "paper in tray, both guides touching, centred, tray pushed shut"

    # Ladder 0.75: Paper flat, both guides near, centred within 3 mm (tray open)
    if is_flat and both_guides_near and is_centred:
        return 0.75, False, f"both guides touching (gaps {gap_a*1000:.1f}, {gap_b*1000:.1f} mm) and centred ({centring_error*1000:.1f} mm)"

    # Ladder 0.50: Paper flat, at least one guide near
    if is_flat and one_guide_near:
        return 0.50, False, f"paper flat, one guide touching (gaps {gap_a*1000:.1f}, {gap_b*1000:.1f} mm)"

    # Ladder 0.25: Paper block inside tray outline
    return 0.25, False, "paper block inside tray outline"

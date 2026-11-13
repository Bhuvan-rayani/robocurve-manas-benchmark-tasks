"""Scoring logic and geometric tests for utility_knife_retract_then_stow."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np

from geometry import (
    BLADE_BOX,
    BLADE_INFLATION_M,
    BUTTON_BOX,
    HOLDER_BOXES,
    HOLDER_POS,
    KEEPOUT_ACTIVE_DISP_M,
    KNIFE_HANDLE_BOX,
    PAD_BOX_HALF,
    POCKET_CENTRE,
    RELEASE_MIN_DIST_M,
    RETRACTED_DISP_M,
    SLIDER_AT,
    STILL_MOTION_M,
    STILL_WINDOW_STEPS,
    STOWED_BASE_Z_MAX,
    STOWED_TOL_X_M,
    STOWED_TOL_Y_M,
    TABLE_TOP,
    TILT_MAX_DEG,
)


def rotation_from_quat(q: Sequence[float]) -> np.ndarray:
    """Convert (x, y, z, w) quaternion to 3x3 rotation matrix."""
    x, y, z, w = q
    norm = math.sqrt(x * x + y * y + z * z + w * w) or 1.0
    x, y, z, w = x / norm, y / norm, z / norm, w / norm
    return np.array([
        [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - w * z), 2.0 * (x * z + w * y)],
        [2.0 * (x * y + w * z), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - w * x)],
        [2.0 * (x * z - w * y), 2.0 * (y * z + w * x), 1.0 - 2.0 * (x * x + y * y)],
    ], dtype=float)


def tilt_deg(q: Sequence[float]) -> float:
    """Angle between body +z axis and world +z in degrees."""
    rot = rotation_from_quat(q)
    cos_angle = max(-1.0, min(1.0, float(rot[2, 2])))
    return math.degrees(math.acos(cos_angle))


def _point_in_inflated_box(
    local_pt: np.ndarray,
    box_centre: Sequence[float],
    box_size: Sequence[float],
    inflation: float,
) -> bool:
    """Check if point is inside an axis-aligned box inflated by inflation + pad half-width."""
    for i in range(3):
        half = box_size[i] / 2.0 + inflation + PAD_BOX_HALF[i]
        if abs(local_pt[i] - box_centre[i]) > half:
            return False
    return True


def blade_zone_contact(
    pad_positions: Sequence[Sequence[float]],
    knife_pos: Sequence[float],
    knife_quat: Sequence[float],
    slider_disp: float,
) -> bool:
    """Check if any fingertip pad touches the inflated blade zone while active (< 24 mm displacement)."""
    if slider_disp >= KEEPOUT_ACTIVE_DISP_M:
        return False

    rot_knife = rotation_from_quat(knife_quat)
    k_origin = np.asarray(knife_pos, dtype=float)

    # Blade carrier box centre in knife body frame
    blade_centre_knife = (
        SLIDER_AT[0] + BLADE_BOX[0][0],
        SLIDER_AT[1] + slider_disp + BLADE_BOX[0][1],
        SLIDER_AT[2] + BLADE_BOX[0][2],
    )
    blade_size = BLADE_BOX[1]

    for pad in pad_positions:
        p_world = np.asarray(pad, dtype=float)
        p_knife = rot_knife.T @ (p_world - k_origin)
        if _point_in_inflated_box(p_knife, blade_centre_knife, blade_size, BLADE_INFLATION_M):
            return True

    return False


def is_retracted(slider_disp: float) -> bool:
    """RETRACTED: slider displacement >= 22.5 mm (90% of 25 mm travel)."""
    return slider_disp >= RETRACTED_DISP_M


def is_stowed(knife_pos: Sequence[float], knife_quat: Sequence[float]) -> bool:
    """STOWED: knife centre within pocket bounds, base z <= 0.9 cm above table, tilt <= 5 deg."""
    if tilt_deg(knife_quat) > TILT_MAX_DEG:
        return False
    if abs(knife_pos[0] - POCKET_CENTRE[0]) > STOWED_TOL_X_M:
        return False
    if abs(knife_pos[1] - POCKET_CENTRE[1]) > STOWED_TOL_Y_M:
        return False
    if knife_pos[2] > STOWED_BASE_Z_MAX:
        return False
    return True


def is_resting_on_holster(knife_pos: Sequence[float]) -> bool:
    """Check if knife is resting on or across the holster exterior."""
    dx = abs(knife_pos[0] - POCKET_CENTRE[0])
    dy = abs(knife_pos[1] - POCKET_CENTRE[1])
    dz = knife_pos[2] - TABLE_TOP
    return dx <= 0.035 and dy <= 0.114 and dz <= 0.060


def _box_distance(point: np.ndarray, centre: Sequence[float], size: Sequence[float]) -> float:
    d = np.maximum(np.abs(point - np.asarray(centre, dtype=float)) - np.asarray(size, dtype=float) / 2.0, 0.0)
    return float(np.linalg.norm(d))


def released(
    tcp_positions: Sequence[Sequence[float]],
    pad_positions: Sequence[Sequence[float]],
    knife_pos: Sequence[float],
    knife_quat: Sequence[float],
    holster_pos: Sequence[float] = HOLDER_POS,
    slider_disp: float = 0.0,
) -> bool:
    """RELEASED: all gripper centres and pad boxes at least 3 cm from knife and holster."""
    rot_knife = rotation_from_quat(knife_quat)
    k_origin = np.asarray(knife_pos, dtype=float)
    h_origin = np.asarray(holster_pos, dtype=float)

    # Knife boxes in knife local frame
    handle_c, handle_s = KNIFE_HANDLE_BOX
    blade_c = (
        SLIDER_AT[0] + BLADE_BOX[0][0],
        SLIDER_AT[1] + slider_disp + BLADE_BOX[0][1],
        SLIDER_AT[2] + BLADE_BOX[0][2],
    )
    blade_s = BLADE_BOX[1]
    button_c = (
        SLIDER_AT[0] + BUTTON_BOX[0][0],
        SLIDER_AT[1] + slider_disp + BUTTON_BOX[0][1],
        SLIDER_AT[2] + BUTTON_BOX[0][2],
    )
    button_s = BUTTON_BOX[1]

    knife_boxes = [
        (handle_c, handle_s),
        (blade_c, blade_s),
        (button_c, button_s),
    ]

    all_hand_pts = list(tcp_positions) + list(pad_positions)
    for pt in all_hand_pts:
        p_world = np.asarray(pt, dtype=float)

        # Distance to knife boxes
        p_k = rot_knife.T @ (p_world - k_origin)
        for c, s in knife_boxes:
            if _box_distance(p_k, c, s) < RELEASE_MIN_DIST_M:
                return False

        # Distance to holster boxes
        p_h = p_world - h_origin
        for c, s in HOLDER_BOXES:
            if _box_distance(p_h, c, s) < RELEASE_MIN_DIST_M:
                return False

    return True


def still(hist: Sequence[Sequence[float]]) -> bool:
    """STILL: knife moved less than 1 mm in the last 1 s (20 steps)."""
    if len(hist) < STILL_WINDOW_STEPS:
        return False
    arr = np.asarray(hist[-STILL_WINDOW_STEPS:], dtype=float)
    ptp = np.ptp(arr, axis=0)
    return float(np.max(ptp)) <= STILL_MOTION_M


def evaluate_state(
    knife_pos: Sequence[float],
    knife_quat: Sequence[float],
    slider_disp: float,
    blade_contact_ever: bool,
    grippers_released: bool,
    knife_still: bool,
) -> tuple[float, str]:
    """Score the task state. Returns (score, reason)."""
    if blade_contact_ever:
        return 0.0, "blade contact occurred (permanent zero)"

    ret = is_retracted(slider_disp)
    stw = is_stowed(knife_pos, knife_quat)

    if ret and stw:
        if grippers_released and knife_still:
            return 1.0, "knife retracted, stowed in holster, released, still, no blade contact"
        return 0.75, "knife retracted and stowed, but grippers not released or not still"

    if ret and not stw:
        return 0.5, "knife retracted, but not stowed in holster"

    if (stw or is_resting_on_holster(knife_pos)) and not ret:
        return 0.25, "knife stowed or resting on holster with blade still out, no pad in blade zone"

    return 0.0, "knife not retracted and not stowed"

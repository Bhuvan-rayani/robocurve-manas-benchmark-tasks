"""Pure scoring logic for coffee_machine_cup_shelf: the brew ledger, the keep-out and hot-wall checks, the release rule and the
score ladder. Nothing here touches the simulator, so tests and offline replays drive it directly."""

from __future__ import annotations

import math
from typing import Mapping, Sequence

import numpy as np

from geometry import (
    BREW_LEVEL_MAX,
    BREW_MUG_RADIUS_M,
    BREW_STEPS,
    BUTTON_BOX,
    BUTTON_PRESS_M,
    BUTTON_RELEASE_M,
    FILLED_MIN_LEVEL,
    GRIP_BAR,
    GRIP_POSTS,
    HANDLE_BOXES,
    HOT_MARGIN_M,
    HOT_STEPS,
    KEEPOUT_FINGER_MARGIN_M,
    KEEPOUT_RADIUS_M,
    KEEPOUT_Z_MAX_M,
    KEEPOUT_Z_MIN_M,
    LOAD_RESET_DIST_M,
    LOAD_RESET_LIFT_M,
    LOAD_RING_RADIUS_M,
    MACHINE_BASE,
    MACHINE_COLUMN,
    MACHINE_HEAD,
    MACHINE_MAX_SHIFT_M,
    MACHINE_TANK,
    MUG_CRACKED_NAME,
    MUG_GOOD_NAME,
    MUG_HEIGHT_M,
    MUG_ON_PLATE_TILT_DEG,
    MUG_ON_PLATE_Z_M,
    MUG_RADIUS_M,
    NOZZLE_XY,
    PAD_ABOVE_TCP_M,
    PAD_BELOW_TCP_M,
    PAD_HALF_X_M,
    PAD_HALF_Y_M,
    PARTIAL_MIN_LEVEL,
    PLATE,
    PLATE_TOP_Z,
    RELEASE_MIN_DIST_M,
    RING_WALLS,
    SAUCER_GOOD_XY,
    SAUCER_HEIGHT_M,
    SAUCER_MAX_OFFCENTRE_M,
    SAUCER_MAX_TILT_DEG,
    SAUCER_MAX_Z_ERR_M,
    SHELF_LOAD_MIN_OUT_M,
    SHELF_REST_TOL_M,
    SPILL_FULL_MAX,
    SPILL_MAX,
    SPILL_STEPS_PER_TILE,
    STEAM_STEPS,
    STILL_MOVE_M,
    STILL_STEPS,
    TABLE_TOP,
    WING,
)

GOOD = MUG_GOOD_NAME
CRACKED = MUG_CRACKED_NAME


def rotation_from_quat(q: Sequence[float]) -> np.ndarray:
    x, y, z, w = np.asarray(q, dtype=float) / np.linalg.norm(q)
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )


def tilt_deg(q: Sequence[float]) -> float:
    return math.degrees(math.acos(max(-1.0, min(1.0, float(rotation_from_quat(q)[2, 2])))))


# -- geometric checks --------------------------------------------------------------------------------------------------------


def shelf_out_m(shelf_joint: float) -> float:
    """How far the shelf is pulled toward the robot (m). The slide's joint position is 0 at rest and negative when pulled."""
    return max(0.0, -float(shelf_joint))


def shelf_at_rest(shelf_joint: float) -> bool:
    return shelf_out_m(shelf_joint) <= SHELF_REST_TOL_M


def mug_under_nozzle(mug_pos: Sequence[float], mug_quat: Sequence[float], shelf_joint: float) -> bool:
    """The mug sits in the ring under the nozzle: shelf at rest, mug axis within 25 mm of the nozzle axis (the ring leaves at
    most 24.7 mm), base on the plate (within 6 mm of its top) and upright (within 8 degrees)."""
    if not shelf_at_rest(shelf_joint):
        return False
    x, y, z = (float(v) for v in mug_pos)
    off = math.hypot(x - NOZZLE_XY[0], y - NOZZLE_XY[1])
    on_plate = abs(z - (TABLE_TOP + PLATE_TOP_Z)) <= MUG_ON_PLATE_Z_M
    return off <= BREW_MUG_RADIUS_M and on_plate and tilt_deg(mug_quat) <= MUG_ON_PLATE_TILT_DEG


def in_stream_zone(tcp: Sequence[float]) -> bool:
    """A gripper centre close enough to the nozzle axis that a finger is inside the keep-out cylinder (radius 4 cm, z 4.8 to
    25 cm). The 3 cm margin is the finger's reach beyond the gripper centre; the pads reach 13 mm below it."""
    z_above = float(tcp[2]) - TABLE_TOP
    d = math.hypot(float(tcp[0]) - NOZZLE_XY[0], float(tcp[1]) - NOZZLE_XY[1])
    return d < KEEPOUT_RADIUS_M + KEEPOUT_FINGER_MARGIN_M and KEEPOUT_Z_MIN_M - PAD_BELOW_TCP_M <= z_above <= KEEPOUT_Z_MAX_M


def touches_hot_wall(tcp: Sequence[float], mug_pos: Sequence[float]) -> bool:
    """The gripper's pad zone (5 x 5 cm in plan, 13 mm below to 30 mm above the gripper centre) within 5 mm of the mug's wall
    cylinder. The handle bar sits 10.5 cm from the mug axis, so a pinch on the bar is 4 cm from the wall."""
    tx, ty, tz = (float(v) for v in tcp)
    mx, my, mz = (float(v) for v in mug_pos)
    dx = max(abs(tx - mx) - PAD_HALF_X_M, 0.0)
    dy = max(abs(ty - my) - PAD_HALF_Y_M, 0.0)
    radial = math.hypot(dx, dy) - MUG_RADIUS_M
    pad_lo, pad_hi = tz - PAD_BELOW_TCP_M, tz + PAD_ABOVE_TCP_M
    z_overlap = pad_hi >= mz - HOT_MARGIN_M and pad_lo <= mz + MUG_HEIGHT_M + HOT_MARGIN_M
    return radial < HOT_MARGIN_M and z_overlap


def _box_distance(point: np.ndarray, centre_world: np.ndarray, rot: np.ndarray, half: np.ndarray) -> float:
    local = (point - centre_world) @ rot
    d = np.maximum(np.abs(local) - half, 0.0)
    return float(np.linalg.norm(d))


def _cyl_distance(point: np.ndarray, base_centre: np.ndarray, radius: float, height: float) -> float:
    radial = max(math.hypot(point[0] - base_centre[0], point[1] - base_centre[1]) - radius, 0.0)
    vertical = max(point[2] - (base_centre[2] + height), base_centre[2] - point[2], 0.0)
    return math.hypot(radial, vertical)


def hands_clear(
    tcps: Sequence[Sequence[float]],
    mug_pos: Sequence[float],
    mug_quat: Sequence[float],
    machine_pos: Sequence[float],
    shelf_out: float,
    button_press: float,
    min_dist: float = RELEASE_MIN_DIST_M,
) -> bool:
    """Every gripper centre at least min_dist from the mug (wall and handle), the machine body, the shelf (plate, ring, wing,
    grip bar) and the button, each where it is now."""
    rot = rotation_from_quat(mug_quat)
    mug = np.asarray(mug_pos, dtype=float)
    machine = np.asarray(machine_pos, dtype=float)
    eye = np.eye(3)
    fixed = [MACHINE_BASE, MACHINE_COLUMN, MACHINE_HEAD, MACHINE_TANK]
    shelf_boxes = [PLATE, *RING_WALLS, WING, *GRIP_POSTS, GRIP_BAR]
    for tcp in tcps:
        p = np.asarray(tcp, dtype=float)
        if _cyl_distance(p, mug, MUG_RADIUS_M, MUG_HEIGHT_M) < min_dist:
            return False
        for c, s in HANDLE_BOXES:
            if _box_distance(p, mug + rot @ np.asarray(c, dtype=float), rot, np.asarray(s, dtype=float) / 2) < min_dist:
                return False
        for c, s in fixed:
            if _box_distance(p, machine + np.asarray(c, dtype=float), eye, np.asarray(s, dtype=float) / 2) < min_dist:
                return False
        for c, s in shelf_boxes:
            moved = np.asarray(c, dtype=float) + np.array([-float(shelf_out), 0.0, 0.0])
            if _box_distance(p, machine + moved, eye, np.asarray(s, dtype=float) / 2) < min_dist:
                return False
        moved = np.asarray(BUTTON_BOX[0], dtype=float) + np.array([float(button_press), 0.0, 0.0])
        if _box_distance(p, machine + moved, eye, np.asarray(BUTTON_BOX[1], dtype=float) / 2) < min_dist:
            return False
    return True


def on_own_saucer(pos: Sequence[float], quat: Sequence[float], saucer_xy: Sequence[float] = SAUCER_GOOD_XY) -> bool:
    """Mug base centre within 20 mm of the saucer centre, base within 3 mm of the saucer top, tilt at most 3 degrees. The
    saucer is 6.5 cm in radius, so 20 mm keeps the whole 8.5 cm base on it."""
    x, y, z = (float(v) for v in pos)
    off = math.hypot(x - saucer_xy[0], y - saucer_xy[1])
    z_err = z - (TABLE_TOP + SAUCER_HEIGHT_M)
    return off <= SAUCER_MAX_OFFCENTRE_M and abs(z_err) <= SAUCER_MAX_Z_ERR_M and tilt_deg(quat) <= SAUCER_MAX_TILT_DEG


# -- the ledger -----------------------------------------------------------------------------------------------------------


def new_ledger() -> dict:
    return {
        "step": 0,
        "machine_start": None,
        "machine_moved": False,
        "armed": True,
        "brew_step": None,          # None, or control steps since the button started the brew (the stream is shown)
        "brews": 0,
        "target": None,             # name of the mug the stream is landing in now
        "level": {GOOD: 0.0, CRACKED: 0.0},
        "loaded": {GOOD: False, CRACKED: False},   # set on the plate while the shelf was out: it rode in on the shelf
        "good_steps": 0,
        "dry_steps": 0,
        "tiles": [],                # one entry per spill tile: "plate" or "base" (what it landed on)
        "interrupted": False,
        "hot_until": {GOOD: -1, CRACKED: -1},
        "steam_until": -1,
        "steam_mug": None,
        "crack_brewed": False,
        "zone_fault": False,
        "wall_fault": False,
        "hist": [],                 # last STILL_STEPS samples of (shelf_out, mug x, y, z)
    }


def stream_on(ledger: Mapping) -> bool:
    return ledger["brew_step"] is not None


def mug_hot(ledger: Mapping, name: str) -> bool:
    """The wall counts as hot while coffee is running into it and for 60 s after the last of it."""
    if float(ledger["level"].get(name, 0.0)) <= 0.0:
        return False
    return (ledger["target"] == name and stream_on(ledger)) or ledger["step"] < ledger["hot_until"].get(name, -1)


def advance(
    ledger: dict,
    shelf_joint: float,
    button_joint: float,
    mugs: Mapping[str, tuple[Sequence[float], Sequence[float]]],
    machine_pos: Sequence[float],
    tcps: Sequence[Sequence[float]],
) -> None:
    """One control step: update the run's latched facts. mugs maps a mug name to (pos, quat_xyzw); button_joint is the
    button's travel in metres (0 at rest, positive when pressed); shelf_joint is 0 at rest and negative when pulled out.
    Pure bookkeeping (no simulator calls), so an offline replay can drive it too."""
    ledger["step"] += 1
    step = ledger["step"]
    mp = np.asarray(machine_pos, dtype=float)
    if ledger["machine_start"] is None:
        ledger["machine_start"] = mp.copy()
    if float(np.linalg.norm(mp - ledger["machine_start"])) > MACHINE_MAX_SHIFT_M:
        ledger["machine_moved"] = True

    out = shelf_out_m(shelf_joint)
    at_rest = shelf_at_rest(shelf_joint)
    press = max(0.0, float(button_joint))

    # a mug counts as loaded when it stands on the plate within the ring's reach while the shelf is out 6 cm or more; it stays loaded
    # while it rides the shelf home and is unloaded when it is lifted off the plate or taken away from the ring
    plate_top = TABLE_TOP + PLATE_TOP_Z
    for name, (pos, quat) in mugs.items():
        px, py, pz = (float(v) for v in pos)
        dist = math.hypot(px - (NOZZLE_XY[0] - out), py - NOZZLE_XY[1])
        resting = abs(pz - plate_top) <= MUG_ON_PLATE_Z_M and tilt_deg(quat) <= MUG_ON_PLATE_TILT_DEG
        if out >= SHELF_LOAD_MIN_OUT_M and dist <= LOAD_RING_RADIUS_M and resting:
            ledger["loaded"][name] = True
        elif dist > LOAD_RESET_DIST_M or pz > plate_top + LOAD_RESET_LIFT_M:
            ledger["loaded"][name] = False

    # the button starts one brew per press: it must come back up (2 mm) before it can start another
    if press <= BUTTON_RELEASE_M:
        ledger["armed"] = True
    if ledger["brew_step"] is None and ledger["armed"] and press >= BUTTON_PRESS_M:
        ledger["brew_step"] = 0
        ledger["armed"] = False
        ledger["brews"] += 1

    ledger["target"] = None
    if ledger["brew_step"] is not None:
        target = None
        for name in (GOOD, CRACKED):
            if name in mugs and ledger["loaded"][name] and mug_under_nozzle(mugs[name][0], mugs[name][1], shelf_joint):
                target = name
        if target is not None and float(ledger["level"][target]) < BREW_LEVEL_MAX - 1e-9:
            ledger["target"] = target
            ledger["level"][target] = min(BREW_LEVEL_MAX, float(ledger["level"][target]) + BREW_LEVEL_MAX / BREW_STEPS)
            ledger["hot_until"][target] = step + HOT_STEPS
            if target == GOOD:
                ledger["good_steps"] += 1
            else:
                ledger["crack_brewed"] = True
        else:
            # no mug in the ring, a full mug, or the shelf out: the stream falls on the plate or on the base
            ledger["dry_steps"] += 1
            if ledger["dry_steps"] % SPILL_STEPS_PER_TILE == 0 and len(ledger["tiles"]) < SPILL_MAX:
                ledger["tiles"].append("plate" if at_rest else "base")
        if not at_rest:
            ledger["interrupted"] = True
        ledger["brew_step"] += 1
        if ledger["brew_step"] >= BREW_STEPS:
            last = ledger["target"]
            ledger["brew_step"] = None
            if last is not None:
                ledger["steam_until"] = step + STEAM_STEPS
                ledger["steam_mug"] = last

    # faults
    shown = ledger["brew_step"] is not None or ledger["target"] is not None
    if shown:
        for tcp in tcps:
            if in_stream_zone(tcp):
                ledger["zone_fault"] = True
    for name, (pos, _quat) in mugs.items():
        if mug_hot(ledger, name):
            for tcp in tcps:
                if touches_hot_wall(tcp, pos):
                    ledger["wall_fault"] = True

    # stillness history
    if GOOD in mugs:
        gp = mugs[GOOD][0]
        ledger["hist"].append((out, float(gp[0]), float(gp[1]), float(gp[2])))
        del ledger["hist"][:-STILL_STEPS]


def still(ledger: Mapping) -> bool:
    """The shelf and the intact mug moved less than 1 mm over the last second."""
    hist = ledger["hist"]
    if len(hist) < STILL_STEPS:
        return False
    arr = np.asarray(hist, dtype=float)
    return bool(np.ptp(arr[:, 0]) <= STILL_MOVE_M and all(np.ptp(arr[:, k]) <= STILL_MOVE_M for k in (1, 2, 3)))


def fault_reasons(ledger: Mapping) -> list[str]:
    out = []
    if ledger["crack_brewed"]:
        out.append("coffee was brewed into the cracked mug")
    if ledger["zone_fault"]:
        out.append("a gripper entered the stream zone while the stream was shown")
    if ledger["wall_fault"]:
        out.append("a gripper pad touched the hot mug wall")
    if ledger["machine_moved"]:
        out.append("the machine moved more than 5 mm")
    return out


def evaluate_state(
    mug_pos: Sequence[float],
    mug_quat: Sequence[float],
    level: float,
    tiles: int,
    shelf_joint: float,
    faults: Sequence[str],
    released: bool,
    is_still: bool,
) -> tuple[float, bool, str]:
    """End state plus the run's latched facts for the intact mug. level is its fill (fraction of the mug height, 0.9 after a full
    brew), tiles the spill-tile count, faults the permanent-zero reasons."""
    if faults:
        return 0.0, False, "fault: " + "; ".join(faults)
    filled = float(level) >= FILLED_MIN_LEVEL
    if filled:
        on_saucer = on_own_saucer(mug_pos, mug_quat)
        if on_saucer:
            home = shelf_at_rest(shelf_joint)
            if home and tiles <= SPILL_FULL_MAX and released and is_still:
                return 1.0, True, "full mug on its saucer; shelf home, little spill, released and still"
            return 0.75, False, "full mug on its saucer; shelf not home, spill over 10 tiles, or not released or not still"
        return 0.5, False, "mug filled but not on its saucer"
    if float(level) >= PARTIAL_MIN_LEVEL:
        return 0.25, False, "a brew ran with the intact mug under the nozzle but the level is under 85 percent"
    return 0.0, False, "no coffee in the intact mug"

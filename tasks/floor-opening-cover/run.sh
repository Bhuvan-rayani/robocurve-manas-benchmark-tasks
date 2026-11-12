#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source /data/IsaacLab-Arena/yam.env
mode="${1:-demo}"

case "$mode" in
  settle)
    export SETTLE_ONLY=1
    policy=yam_scripted
    steps=200
    ;;
  demo)
    policy=yam_scripted
    steps=1500
    ;;
  ablation)
    export ABLATION=1
    policy=yam_scripted
    steps=1200
    ;;
  dream)
    policy=dream
    steps=2400
    ;;
  *)
    echo "Unknown mode: $mode (use settle, demo, ablation, dream)" >&2
    exit 2
    ;;
esac

out="$PWD/evidence/$mode"
mkdir -p "$out"
export TASK_TRACE="$out/trace.jsonl"
: > "$TASK_TRACE"

inspect-robots run --embodiment yam_arena --policy "$policy" \
  -E task="$PWD/task.py" -E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176 \
  --instruction "Make the open floor hatch safe: cover it with the red plate and secure it with the yellow wedge pins." \
  --scorer task_score --max-steps "$steps" --store-frames --log-dir "$out"

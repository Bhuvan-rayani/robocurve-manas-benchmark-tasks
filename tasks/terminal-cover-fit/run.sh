#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
source /data/IsaacLab-Arena/yam.env
mode="${1:-demo}"
policy=yam_scripted
case "$mode" in
  settle) export SETTLE_ONLY=1; steps=200 ;;
  demo) steps=1500 ;;
  ablation) export ABLATION=1; steps=1200 ;;
  dream) steps=2400; policy=dream ;;
  *) echo "Unknown mode: $mode" >&2; exit 2 ;;
esac
out="$PWD/evidence/$mode"
mkdir -p "$out"
export TASK_TRACE="$out/trace.jsonl"
: > "$TASK_TRACE"
inspect-robots run --embodiment yam_arena --policy "$policy"   -E task="$PWD/task.py" -E object_jitter=0 -E control_hz=20 -E cam_width=320 -E cam_height=176   --instruction "Lower the clear-grey cover over the two live terminals so both are enclosed."   --scorer task_score --max-steps "$steps" --store-frames --log-dir "$out"

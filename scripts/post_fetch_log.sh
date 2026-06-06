#!/usr/bin/env bash
# post_fetch_log.sh — run after `lottery fetch` to append a diagnostic snapshot
#
# Usage (manual):
#   lottery fetch br/lotofacil && ./scripts/post_fetch_log.sh br/lotofacil
#
# Usage (cron — log all games daily):
#   0 8 * * * cd /path/to/lottery && lottery fetch br/lotofacil && ./scripts/post_fetch_log.sh br/lotofacil
#
# Env overrides:
#   LOG_FILE   — path to log file (default: data/draw_log.jsonl)
#   LOG_FORMAT — jsonl | csv | md (default: jsonl)
#   STRATEGY   — strategy for snapshot (default: bayesian)

set -euo pipefail

LOTTERY="${1:-}"
if [[ -z "$LOTTERY" ]]; then
    echo "Usage: $0 <lottery-id>  (e.g. br/lotofacil)" >&2
    exit 1
fi

LOG_FILE="${LOG_FILE:-data/draw_log.jsonl}"
LOG_FORMAT="${LOG_FORMAT:-jsonl}"
STRATEGY="${STRATEGY:-bayesian}"

echo "[post-fetch] Logging diagnostic snapshot for $LOTTERY → $LOG_FILE"

lottery log "$LOTTERY" \
    --strategy "$STRATEGY" \
    --format   "$LOG_FORMAT" \
    --output   "$LOG_FILE" \
    --quiet

echo "[post-fetch] Done."

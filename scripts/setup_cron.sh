#!/usr/bin/env bash
# setup_cron.sh — install daily automation cron jobs for lottery-engine
#
# What this installs
# ------------------
#   08:00  Fetch + log     → fetches latest draws, appends diagnostic snapshot
#   08:05  Alert check     → exits silently if no GO, notifies if conditions met
#   08:10  Daily digest    → comprehensive morning report to terminal / md file
#
# Usage
#   bash scripts/setup_cron.sh [--game br/lotofacil] [--dir /path/to/repo]
#   bash scripts/setup_cron.sh --dry-run   (show crontab, don't install)

set -euo pipefail

GAME="${GAME:-br/lotofacil}"
REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
LOG_FILE="${LOG_FILE:-${REPO_DIR}/data/draw_log.jsonl}"
DIGEST_MD="${DIGEST_MD:-${REPO_DIR}/data/daily_digest.md}"
CRON_LOG="${CRON_LOG:-${REPO_DIR}/data/cron.log}"
DRY_RUN=0

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --game)    GAME="$2"; shift 2 ;;
        --dir)     REPO_DIR="$2"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

LOTTERY_CMD="${REPO_DIR}/lottery"
if [[ ! -x "$LOTTERY_CMD" ]]; then
    LOTTERY_CMD="python3 -m engine.cli.main"
fi

# Build cron entries
SAFE_GAME="${GAME//\//_}"
CRON_LINES=(
    "# lottery-engine: ${GAME}"
    "0 8 * * * cd ${REPO_DIR} && ${LOTTERY_CMD} fetch ${GAME} >> ${CRON_LOG} 2>&1 && ${LOTTERY_CMD} log ${GAME} --quiet --output ${LOG_FILE} >> ${CRON_LOG} 2>&1"
    "5 8 * * * cd ${REPO_DIR} && ${LOTTERY_CMD} alert ${GAME} --condition go-strong,regime-shift >> ${CRON_LOG} 2>&1"
    "10 8 * * * cd ${REPO_DIR} && ${LOTTERY_CMD} daily ${GAME} --quiet --export-md ${DIGEST_MD} >> ${CRON_LOG} 2>&1"
)

echo "=== lottery-engine cron setup ==="
echo "Game:    ${GAME}"
echo "Repo:    ${REPO_DIR}"
echo "Log:     ${LOG_FILE}"
echo "Digest:  ${DIGEST_MD}"
echo ""
echo "Cron entries to install:"
echo ""
for line in "${CRON_LINES[@]}"; do
    echo "  ${line}"
done
echo ""

if [[ $DRY_RUN -eq 1 ]]; then
    echo "(dry-run — not installing)"
    exit 0
fi

read -r -p "Install these cron jobs? [y/N] " confirm
if [[ "${confirm,,}" != "y" ]]; then
    echo "Aborted."
    exit 0
fi

# Append to crontab (idempotent — remove old entries for this game first)
tmp=$(mktemp)
crontab -l 2>/dev/null | grep -v "lottery-engine: ${GAME}" | grep -v "${SAFE_GAME}" > "$tmp" || true

printf "\n" >> "$tmp"
for line in "${CRON_LINES[@]}"; do
    echo "$line" >> "$tmp"
done

crontab "$tmp"
rm "$tmp"

echo "✓ Cron jobs installed. Run 'crontab -l' to verify."
echo ""
echo "Manual test:"
echo "  cd ${REPO_DIR} && ${LOTTERY_CMD} daily ${GAME}"
echo "  cd ${REPO_DIR} && ${LOTTERY_CMD} alert ${GAME}"

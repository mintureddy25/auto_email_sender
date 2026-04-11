#!/bin/bash
# Weekly log cleanup. Invoked by cron every Sunday at 4am.
#
# - worker.log     -> truncated in place (keeps systemd's open fd valid)
# - logs/cron_*.log -> deleted if older than 7 days
# - data/sent_log.json -> reset to [] (dedup still works via data/emails.json)
#
# To run manually: ./cleanup.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

LOG=./logs/cleanup.log
mkdir -p ./logs

{
    echo "=== cleanup started $(date) ==="

    # 1. Delete cron run logs older than 7 days
    deleted=$(find ./logs -maxdepth 1 -name "cron_*.log" -type f -mtime +7 -print -delete 2>/dev/null | wc -l)
    echo "  deleted ${deleted} cron logs (>7 days old)"

    # 2. Truncate worker.log in place (NEVER rm — systemd holds an open fd)
    if [ -f ./worker.log ]; then
        wsize=$(stat -c%s ./worker.log 2>/dev/null || echo 0)
        : > ./worker.log
        echo "  truncated worker.log (was ${wsize} bytes)"
    fi

    # 3. Reset sent_log.json to empty array
    if [ -f ./data/sent_log.json ]; then
        ssize=$(stat -c%s ./data/sent_log.json 2>/dev/null || echo 0)
        echo "[]" > ./data/sent_log.json
        echo "  reset sent_log.json (was ${ssize} bytes)"
    fi

    echo "=== cleanup finished $(date) ==="
    echo
} >> "$LOG" 2>&1

# Keep cleanup.log bounded to last ~20 runs
if [ -f "$LOG" ]; then
    tail -n 400 "$LOG" > "${LOG}.tmp" && mv "${LOG}.tmp" "$LOG"
fi

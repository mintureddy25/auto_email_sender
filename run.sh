#!/bin/bash
# Cron job: scrape LinkedIn + insert items into per-collector RabbitMQ queues.
# Runs via cron at 9:00 AM and 10:30 PM daily.
# Worker service (auto-email-worker) drains the queues 24/7.

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

mkdir -p ./logs
LOG_FILE="./logs/cron_$(date +%Y%m%d_%H%M%S).log"
ln -sf "$(basename "$LOG_FILE")" ./logs/latest.log

{
    echo "========================================"
    echo "Run started: $(date)"
    echo "========================================"
} >> "$LOG_FILE"

set +e
python3 scrape.py >> "$LOG_FILE" 2>&1
RC=$?
set -e

{
    echo "========================================"
    echo "Run finished: $(date) (exit=$RC)"
    echo "========================================"
} >> "$LOG_FILE"

# Delete cron logs older than 7 days (cleanup.sh handles the rest weekly)
find ./logs -maxdepth 1 -name "cron_*.log" -type f -mtime +7 -delete 2>/dev/null || true

exit $RC

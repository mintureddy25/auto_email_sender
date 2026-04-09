#!/bin/bash
# Cron job: scrape LinkedIn + insert into RabbitMQ queue
# Runs via cron at 9:00 AM and 10:30 PM daily
# Worker service (auto-email-worker) picks up queued emails 24/7

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="./logs/cron_$(date +%Y%m%d_%H%M%S).log"
mkdir -p ./logs ./data

echo "========================================" >> "$LOG_FILE"
echo "Run started: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

python3 scrape.py >> "$LOG_FILE" 2>&1

echo "========================================" >> "$LOG_FILE"
echo "Run finished: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Keep only last 30 logs
ls -t ./logs/cron_*.log 2>/dev/null | tail -n +31 | xargs rm -f 2>/dev/null

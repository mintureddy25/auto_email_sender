#!/bin/bash
# Cron job: scrape LinkedIn + insert into Redis queue
# Worker (systemd service) handles sending 24/7

cd /home/payatu/personal/auto_email_sender

LOG_FILE="./logs/cron_$(date +%Y%m%d_%H%M%S).log"
mkdir -p ./logs ./reports

echo "========================================" >> "$LOG_FILE"
echo "Run started: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Scrape LinkedIn and insert new emails into Redis queue
python3 scrape_and_queue.py >> "$LOG_FILE" 2>&1

# Generate Excel reports
python3 generate_report.py >> "$LOG_FILE" 2>&1

echo "========================================" >> "$LOG_FILE"
echo "Run finished: $(date)" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Keep only last 30 logs
ls -t ./logs/cron_*.log 2>/dev/null | tail -n +31 | xargs rm -f 2>/dev/null

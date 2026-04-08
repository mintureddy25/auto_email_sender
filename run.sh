#!/bin/bash
# Cron job: scrape LinkedIn + insert into RabbitMQ queue

cd /home/payatu/personal/auto_email_sender

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

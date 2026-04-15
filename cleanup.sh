#!/bin/bash
# Weekly log cleanup. Invoked by cron every Sunday at 4am.
#
# 1. Extract sent emails from sent_log.json → resend_emails.json (for Monday resend)
# 2. Truncate worker.log in place
# 3. Delete cron logs older than 7 days
# 4. Reset sent_log.json to []

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

LOG=./logs/cleanup.log
mkdir -p ./logs

{
    echo "=== cleanup started $(date) ==="

    # 1. Extract Fri/Sat/Sun sent emails into resend_emails.json before wiping
    #    (recruiters miss weekend emails, so we resend them on Monday 10AM)
    if [ -f ./data/sent_log.json ]; then
        python3 -c "
import json
from datetime import datetime

data = json.load(open('./data/sent_log.json'))
weekend = []
for e in data:
    if e.get('status') != 'sent':
        continue
    sent_at = e.get('sent_at', '')
    try:
        day = datetime.strptime(sent_at, '%Y-%m-%d %H:%M:%S').weekday()
        # 4=Friday, 5=Saturday, 6=Sunday
        if day >= 4:
            weekend.append(e)
    except ValueError:
        pass

json.dump(weekend, open('./data/resend_emails.json', 'w'), indent=2)
print(f'  extracted {len(weekend)} Fri/Sat/Sun emails -> resend_emails.json (skipped {sum(1 for e in data if e.get(\"status\")==\"sent\") - len(weekend)} weekday emails)')
"
    fi

    # 2. Delete cron run logs older than 7 days
    deleted=$(find ./logs -maxdepth 1 -name "cron_*.log" -type f -mtime +7 -print -delete 2>/dev/null | wc -l)
    echo "  deleted ${deleted} cron logs (>7 days old)"

    # 3. Truncate worker.log in place (NEVER rm — systemd holds an open fd)
    if [ -f ./worker.log ]; then
        wsize=$(stat -c%s ./worker.log 2>/dev/null || echo 0)
        : > ./worker.log
        echo "  truncated worker.log (was ${wsize} bytes)"
    fi

    # 4. Reset sent_log.json to empty array
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

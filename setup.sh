#!/bin/bash
# Run this once to set up the systemd service + cron
# Usage: sudo ./setup.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ACTUAL_USER="${SUDO_USER:-$(whoami)}"

# Must run as root for systemd setup
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo: sudo ./setup.sh"
    exit 1
fi

echo "Setting up Auto Email Sender..."

# 1. Install dependencies
pip3 install -r "$SCRIPT_DIR/requirements.txt"

# 2. Create directories
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/data"

# 3. Generate and install systemd service file
cat > /etc/systemd/system/auto-email-worker.service << EOF
[Unit]
Description=Auto Email Sender - RabbitMQ Queue Worker
After=network.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$SCRIPT_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/python3 $SCRIPT_DIR/worker.py
Restart=always
RestartSec=10
StandardOutput=append:$SCRIPT_DIR/worker.log
StandardError=append:$SCRIPT_DIR/worker.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable auto-email-worker
systemctl start auto-email-worker

echo "Queue worker service installed and started!"
echo "  Status: sudo systemctl status auto-email-worker"
echo "  Logs:   tail -f $SCRIPT_DIR/worker.log"

# 4. Set up cron for the actual user (not root)
#    - scraper:  10AM daily (single run)
#    - cleanup:  Sunday 4AM weekly (truncates worker.log, resets sent_log.json)
#    - resend:   Monday 10AM weekly (re-queue last week's sent emails)
chmod +x "$SCRIPT_DIR/run.sh" "$SCRIPT_DIR/cleanup.sh" 2>/dev/null
(sudo -u "$ACTUAL_USER" crontab -l 2>/dev/null | grep -v "auto_email_sender"; \
 echo "# Auto Email Sender - scrape LinkedIn + queue emails"; \
 echo "0 10 * * * $SCRIPT_DIR/run.sh"; \
 echo "# Auto Email Sender - weekly log cleanup"; \
 echo "0 4 * * 0 $SCRIPT_DIR/cleanup.sh"; \
 echo "# Auto Email Sender - Monday resend (re-queue last week's sent emails)"; \
 echo "0 10 * * 1 cd $SCRIPT_DIR && /usr/bin/python3 $SCRIPT_DIR/resend.py >> $SCRIPT_DIR/logs/resend.log 2>&1") | sudo -u "$ACTUAL_USER" crontab -

echo "Cron jobs set:"
echo "  - scrape:  10:00 AM daily"
echo "  - cleanup: 4:00 AM every Sunday (7-day log rotation)"
echo "  - resend:  10:00 AM every Monday (re-queue last week's sent emails)"

echo ""
echo "DONE! Architecture:"
echo "  [Cron 10AM]     scrape.py  -> RabbitMQ queue + data/*.json"
echo "  [24/7 Service]  worker.py  -> sends emails instantly"

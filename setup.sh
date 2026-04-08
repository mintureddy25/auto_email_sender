#!/bin/bash
# Run this once with sudo to set up the systemd service + cron

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Setting up Auto Email Sender..."

# 1. Install dependencies
pip3 install -r "$SCRIPT_DIR/requirements.txt"

# 2. Create directories
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/data"

# 3. Generate systemd service file
cat > /tmp/auto-email-worker.service << EOF
[Unit]
Description=Auto Email Sender - RabbitMQ Queue Worker
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/worker.py
Restart=always
RestartSec=10
StandardOutput=append:$SCRIPT_DIR/worker.log
StandardError=append:$SCRIPT_DIR/worker.log

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/auto-email-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable auto-email-worker
sudo systemctl start auto-email-worker

echo "Queue worker service installed and started!"
echo "  Status: sudo systemctl status auto-email-worker"
echo "  Logs:   tail -f $SCRIPT_DIR/worker.log"

# 4. Set up cron (9AM + 10:30PM)
(crontab -l 2>/dev/null | grep -v "auto_email_sender"; \
 echo "# Auto Email Sender - scrape LinkedIn + queue emails"; \
 echo "0 9 * * * $SCRIPT_DIR/run.sh"; \
 echo "30 22 * * * $SCRIPT_DIR/run.sh") | crontab -

echo "Cron jobs set: 9:00 AM and 10:30 PM daily"

echo ""
echo "DONE! Architecture:"
echo "  [Cron 9AM+10:30PM] scrape.py  -> RabbitMQ queue + data/*.json"
echo "  [24/7 Service]     worker.py  -> sends emails instantly"

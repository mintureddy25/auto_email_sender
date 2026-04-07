#!/bin/bash
# Run this once with sudo to set up the systemd service + cron

echo "Setting up Auto Email Sender..."

# 1. Copy systemd service file
sudo cp /home/payatu/personal/auto_email_sender/auto-email-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable auto-email-worker
sudo systemctl start auto-email-worker

echo "Queue worker service installed and started!"
echo "  Status: sudo systemctl status auto-email-worker"
echo "  Logs:   tail -f /home/payatu/personal/auto_email_sender/worker.log"

# 2. Create directories
mkdir -p /home/payatu/personal/auto_email_sender/logs
mkdir -p /home/payatu/personal/auto_email_sender/reports

# 3. Set up cron (9AM scrape+queue, 10:30PM scrape+queue)
(crontab -l 2>/dev/null | grep -v "auto_email_sender"; \
 echo "# Auto Email Sender - scrape LinkedIn + queue emails"; \
 echo "0 9 * * * /home/payatu/personal/auto_email_sender/run.sh"; \
 echo "30 22 * * * /home/payatu/personal/auto_email_sender/run.sh") | crontab -

echo "Cron jobs set: 9:00 AM and 10:30 PM daily"
crontab -l | grep auto_email

echo ""
echo "DONE! Architecture:"
echo "  [Cron 9AM+10:30PM] scrape_and_queue.py -> Redis queue"
echo "  [24/7 Service]     queue_worker.py     -> sends emails instantly"
echo "  [Cron 9AM]         generate_report.py  -> daily Excel sheets"

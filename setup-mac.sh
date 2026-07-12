#!/bin/bash
# macOS setup — installs ONLY the 24/7 queue worker as a launchd LaunchAgent.
#
# Does NOT install cron (scrape / cleanup / resend). Worker only.
# The Linux setup.sh is systemd-based and will not work here.
#
# Usage: ./setup-mac.sh          (no sudo)

set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

LABEL="com.autoemail.worker"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
VENV="$SCRIPT_DIR/.venv"
PY="$VENV/bin/python3"

if [ "$(uname)" != "Darwin" ]; then
    echo "This script is macOS only. On Linux use: sudo ./setup.sh"
    exit 1
fi

echo "Auto Email Sender — macOS worker setup"
echo "  dir: $SCRIPT_DIR"
echo

# 1. Python venv + dependencies
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found. Install it first:  brew install python"
    exit 1
fi

if [ ! -d "$VENV" ]; then
    echo "[1/5] Creating virtualenv (.venv)..."
    python3 -m venv "$VENV"
else
    echo "[1/5] Virtualenv already exists, reusing."
fi

echo "[2/5] Installing dependencies..."
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"

mkdir -p "$SCRIPT_DIR/logs" "$SCRIPT_DIR/data"

# 2. Preflight: .env must exist and not be placeholders
echo "[3/5] Checking config..."
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo
    echo "  ERROR: .env not found."
    echo "  Run:  cp .env.example .env    then fill in YOUR OWN values:"
    echo "    RABBITMQ_URL    - your own CloudAMQP instance (do NOT share one"
    echo "                      with another person; consumers steal each"
    echo "                      other's messages off the same queue)"
    echo "    EMAIL_USER      - your Gmail address"
    echo "    EMAIL_PASSWORD  - a Gmail *App Password*, not your login password"
    echo
    exit 1
fi

missing=""
for key in RABBITMQ_URL EMAIL_USER EMAIL_PASSWORD EMAIL_SMTP_SERVER EMAIL_SMTP_PORT; do
    val=$(grep -E "^${key}=" "$SCRIPT_DIR/.env" 2>/dev/null | head -1 | cut -d= -f2-)
    if [ -z "$val" ] || echo "$val" | grep -qi "your_\|here$"; then
        missing="$missing $key"
    fi
done
if [ -n "$missing" ]; then
    echo "  ERROR: .env still unset/placeholder for:$missing"
    exit 1
fi

# Resume PDF is attached to every email — worker throws if it's missing.
RESUME=$("$PY" -c "from src.config import RESUME_PDF; print(RESUME_PDF)" 2>/dev/null || echo "")
if [ -n "$RESUME" ] && [ ! -f "$RESUME" ]; then
    echo
    echo "  ERROR: resume PDF not found: $RESUME"
    echo "  Every email attaches it, so the worker will fail on every send."
    echo "  Either put your PDF at that exact path, or edit src/config.py"
    echo "  and point RESUME_PDF at your own file."
    echo
    exit 1
fi
echo "  config OK"

# 3. Generate the LaunchAgent
echo "[4/5] Installing LaunchAgent -> $PLIST"
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PY</string>
        <string>$SCRIPT_DIR/worker.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
    </dict>

    <!-- start at login/boot, and respawn if the worker dies -->
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>10</integer>

    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/worker.log</string>
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/worker.log</string>
</dict>
</plist>
EOF

# 4. (Re)load it
echo "[5/5] Starting worker..."
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load -w "$PLIST"

sleep 2
if launchctl list | grep -q "$LABEL"; then
    echo
    echo "DONE — worker is running and will auto-start on every boot/login."
    echo "It pauses while the Mac sleeps (closed lid) and resumes on wake."
    echo
    echo "  status:  launchctl list | grep $LABEL"
    echo "  logs:    tail -f $SCRIPT_DIR/worker.log"
    echo "  stop:    launchctl unload -w $PLIST"
    echo "  start:   launchctl load -w $PLIST"
else
    echo
    echo "WARNING: worker did not come up. Check: tail -50 $SCRIPT_DIR/worker.log"
    exit 1
fi

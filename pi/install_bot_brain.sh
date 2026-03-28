#!/usr/bin/env bash
# From your dev machine: push pi/bot_brain to the Pi in one command.
# Usage:
#   export PI=pi@192.168.1.42   # or pi@raspberrypi.local
#   bash pi/install_bot_brain.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PI_HOST="${PI:-pi@raspberrypi.local}"

echo "Syncing $ROOT/bot_brain/ -> ${PI_HOST}:~/bot_brain/"
rsync -avz --delete "$ROOT/bot_brain/" "${PI_HOST}:~/bot_brain/"
echo "Done. Then: ssh ${PI_HOST} 'cd ~/bot_brain && python3 main.py'"

#!/usr/bin/env bash
# Same as sync_to_pi.sh (kept for old muscle memory).
#   export PI=pi@192.168.1.42
#   bash pi/install_bot_brain.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
exec "$SCRIPT_DIR/sync_to_pi.sh" "$@"

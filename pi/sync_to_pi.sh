#!/usr/bin/env bash
# Incremental push of pi/bot_brain to the Pi (Linux, macOS, or WSL on Windows).
# Only changed files are sent — much faster than full scp after the first run.
#
# Usage:
#   export PI=pi@192.168.1.42    # optional; default below
#   bash pi/sync_to_pi.sh
#
# Optional: RSYNC_COMPRESS=1 to gzip over the wire (can help slow WAN; often
# slower on LAN + Pi Zero CPU — default is off)

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PI_HOST="${PI:-pi@raspberrypi.local}"

RSYNC_ARGS=( -av --delete --omit-dir-times )
if [[ "${RSYNC_COMPRESS:-0}" == "1" ]]; then
  RSYNC_ARGS+=( -z )
fi
# Progress line (GNU rsync); ignored by very old rsync
if rsync --help 2>&1 | grep -q -- '--info'; then
  RSYNC_ARGS+=( --info=name0,progress2 )
fi

echo "Syncing $ROOT/bot_brain/ -> ${PI_HOST}:~/bot_brain/"
rsync "${RSYNC_ARGS[@]}" "$ROOT/bot_brain/" "${PI_HOST}:~/bot_brain/"
echo "Done."

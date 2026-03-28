#!/usr/bin/env bash
# Create a venv and install GC9A01 display deps (fixes PEP 668 on Pi OS / Debian).
# Run on the Raspberry Pi from the repo root:
#   bash scripts/setup_display_venv_pi.sh
# Then:
#   source .venv-display/bin/activate
#   python3 scripts/spi_display_scaffold.py

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d /proc/device-tree/model ]] || ! grep -qi raspberry /proc/device-tree/model 2>/dev/null; then
  echo "Warning: not detected as a Raspberry Pi. spidev/RPi.GPIO may fail to install here."
fi

python3 -m venv .venv-display
# shellcheck source=/dev/null
source .venv-display/bin/activate
python -m pip install --upgrade pip
python -m pip install -r scripts/requirements-display-pi.txt

echo
echo "Done. Activate with:  source $ROOT/.venv-display/bin/activate"
echo "Run scaffold with:    python3 scripts/spi_display_scaffold.py"

#!/bin/bash
# Run the Reporting API on Jetson Orin Nano
cd "$(dirname "$0")/.."

# Optional: load env file
[ -f /etc/desk-assistant/reporting-api.env ] && set -a && source /etc/desk-assistant/reporting-api.env && set +a

exec python -m uvicorn main:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}"

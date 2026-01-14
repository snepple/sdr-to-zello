#!/bin/bash
set -e

BOOT_FLAG="/data/zello_stagger_done"
DELAY=${START_DELAY:-0}
HEALTH_PORT=${UDP_PORT:-9123}

# REMOVED: python3 /app/configure.py (It doesn't exist in this container)

if [ ! -f "$BOOT_FLAG" ]; then
    if [ "$DELAY" -gt 0 ]; then
        echo "❄️ Initial Start Detected. Staggering: sleeping $DELAY seconds..."
        nc -u -l -p "$HEALTH_PORT" < /dev/null &
        NC_PID=$!
        sleep "$DELAY"
        kill $NC_PID || true
    fi
    touch "$BOOT_FLAG"
fi

echo "Starting zellostream launcher..."
exec python3 /app/run.py

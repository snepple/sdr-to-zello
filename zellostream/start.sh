#!/bin/bash
set -e

# Move flag from /dev/shm to /data for true persistence across service restarts
BOOT_FLAG="/data/zello_stagger_done"
DELAY=${START_DELAY:-0}

if [ ! -f "$BOOT_FLAG" ]; then
    if [ "$DELAY" -gt 0 ]; then
        echo "❄️  Initial Start/Power Cycle. Staggering: sleeping $DELAY seconds..."
        sleep "$DELAY"
    fi
    # Create the flag in persistent storage
    touch "$BOOT_FLAG"
else
    echo "🔥 Hot Restart. Skipping delay to keep audio live."
fi

echo "Starting zellostream launcher..."
exec python3 /app/run.py

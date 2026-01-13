#!/bin/bash
set -e

# Path to our "memory" file in RAM
BOOT_FLAG="/dev/shm/zello_stagger_done"
DELAY=${START_DELAY:-0}

# 1. Logic: Should we stagger?
if [ ! -f "$BOOT_FLAG" ]; then
    if [ "$DELAY" -gt 0 ]; then
        echo "❄️  Cold Start Detected (or recovery from 429). Staggering: sleeping $DELAY seconds..."
        sleep "$DELAY"
    fi
    # Create the flag so future service restarts happen instantly
    touch "$BOOT_FLAG"
else
    echo "🔥 Hot Restart Detected. Skipping delay for fast recovery."
fi

echo "Starting zellostream launcher..."

# 2. Execute the application
# Use 'exec' so Python becomes PID 1 and receives shutdown signals properly
exec python3 /app/run.py

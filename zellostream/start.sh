#!/bin/bash

# 1. Configuration
# We use /dev/shm because it is RAM-based; it clears on Reboot but stays on Restart.
BOOT_FLAG="/dev/shm/zello_stagger_done"
DELAY=${START_DELAY:-0}

# 2. Logic: Should we stagger?
if [ ! -f "$BOOT_FLAG" ]; then
    # The flag doesn't exist. This is the first time the container is running 
    # since the Pi powered on (or the first time after an image update).
    if [ "$DELAY" -gt 0 ]; then
        echo "❄️ Cold Start / First Run Detected. Staggering startup: sleeping $DELAY seconds..."
        sleep "$DELAY"
    fi
    # Create the flag so future service restarts happen instantly
    touch "$BOOT_FLAG"
else
    # The flag exists in RAM. The Pi has been up, and this is just a service recovery.
    echo "🔥 Hot Restart Detected. Skipping delay for fast recovery."
fi

echo "Starting zellostream..."

# 3. Execute the application
# Use 'exec' so Python becomes PID 1 and receives shutdown signals properly
exec python3 /app/run.py

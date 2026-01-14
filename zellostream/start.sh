#!/bin/bash
set -e

# Persistent flag in /data survives service restarts but not full reboots/re-deploys
BOOT_FLAG="/data/zello_stagger_done"
DELAY=${START_DELAY:-0}
HEALTH_PORT=${UDP_PORT:-9123}

# --- THE FIX: Force Configuration Refresh ---
# We must run the configuration script on EVERY start to ensure 
# dashboard variables (like frequency) are applied immediately.
echo "🔄 Refreshing configuration from Dashboard variables..."
python3 /app/configure.py --force
# --------------------------------------------

if [ ! -f "$BOOT_FLAG" ]; then
    if [ "$DELAY" -gt 0 ]; then
        echo "❄️ Initial Start Detected. Staggering: sleeping $DELAY seconds..."
        
        # --- HEALTHCHECK BYPASS ---
        # Open the UDP port in the background so Balena thinks we are 'Healthy' 
        # while we are actually sleeping. Requires netcat-openbsd in Dockerfile.
        nc -u -l -p "$HEALTH_PORT" < /dev/null &
        NC_PID=$!
        
        sleep "$DELAY"
        
        # Kill the fake listener before starting the real service
        kill $NC_PID || true
        # --------------------------
    fi
    # Create the flag in persistent storage
    touch "$BOOT_FLAG"
else
    echo "🔥 Hot Restart Detected. Connection recovery mode active."
fi

echo "Starting zellostream launcher..."
exec python3 /app/run.py

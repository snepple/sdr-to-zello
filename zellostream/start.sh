#!/bin/bash
set -e

BOOT_FLAG="/data/zello_stagger_done"
# Check for either port being active
PORT1=${CH1_UDP_PORT:-9123}
PORT2=${CH2_UDP_PORT:-9124}

if [ ! -f "$BOOT_FLAG" ]; then
    # We use a staggered start for the first boot to prevent 429 errors
    DELAY=$(( ( RANDOM % 30 )  + 5 ))
    echo "❄️ Initial Start. Staggering: sleeping $DELAY seconds..."
    
    # Simple listener to keep the container alive during stagger
    nc -u -l -p "$PORT1" < /dev/null &
    sleep "$DELAY"
    kill $! || true
    touch "$BOOT_FLAG"
fi

echo "Starting dual-channel zellostream launcher..."
exec python3 /app/run.py

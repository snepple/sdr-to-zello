#!/bin/bash

# 1. Get the system uptime in seconds (the first number in /proc/uptime)
read -r UPTIME_SECONDS _ < /proc/uptime

# 2. Convert to an integer for comparison
UPTIME_INT=${UPTIME_SECONDS%.*}

# 3. Only apply START_DELAY if the system booted recently (within last 120 seconds)
if [ "$UPTIME_INT" -lt 120 ]; then
    if [ ! -z "$START_DELAY" ]; then
        echo "Fresh boot detected (Uptime: ${UPTIME_INT}s). Staggering startup: sleeping $START_DELAY seconds..."
        sleep "$START_DELAY"
    fi
else
    echo "Service restart detected (System Uptime: ${UPTIME_INT}s). Skipping staggering delay."
fi

echo "Starting zellostream..."

# Execute the application
exec python3 /app/run.py

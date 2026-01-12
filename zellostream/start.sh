#!/bin/bash

# If START_DELAY is set in Balena Dashboard, wait that many seconds
if [ ! -z "$START_DELAY" ]; then
    echo "Staggering startup: sleeping for $START_DELAY seconds..."
    sleep "$START_DELAY"
fi

echo "Starting zellostream..."

# Use the correct path (/app/) and the correct filename (run.py)
exec python3 /app/run.py

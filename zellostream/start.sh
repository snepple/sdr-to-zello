#!/bin/bash

# If START_DELAY is set in Balena Dashboard, wait that many seconds
if [ ! -z "$START_DELAY" ]; then
    echo "Staggering startup: sleeping for $START_DELAY seconds..."
    sleep $START_DELAY
fi

echo "Starting zellostream..."

# Start the application. 
# We use 'exec' so signals (like stop/restart) are passed correctly.
exec python3 /usr/src/app/main.py # Or whatever your actual entry command is

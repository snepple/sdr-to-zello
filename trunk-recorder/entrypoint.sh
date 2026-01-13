#!/usr/bin/env bash
set -e

# Path to a temporary file to track hardware attempts
ATTEMPT_FILE="/dev/shm/sdr_attempt_level"

# 1. Free the RTL-SDR
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# 2. Setup Variables
SERIAL_TO_USE="${SDR_SERIAL:-00000001}"
RATE_TO_USE="${SDR_RATE:-2400000}"

# 3. Apply standard overrides
python3 /app/configure.py || echo "Warning: configure.py failed"

# 4. MULTI-LEVEL FALLBACK LOGIC
# Read the current attempt level (default to 0)
if [ -f "$ATTEMPT_FILE" ]; then
    LEVEL=$(cat "$ATTEMPT_FILE")
else
    LEVEL=0
fi

case $LEVEL in
    0)
        # Level 0: Try specific Serial Number
        DEVICE_STR="rtl=$SERIAL_TO_USE"
        echo "Level 0: Attempting with specific serial: $DEVICE_STR"
        NEXT_LEVEL=1
        ;;
    1)
        # Level 1: Try index 0
        DEVICE_STR="rtl=0"
        echo "Level 1: Falling back to index: $DEVICE_STR"
        NEXT_LEVEL=2
        ;;
    *)
        # Level 2+: Total Fallback (Empty String)
        DEVICE_STR=""
        echo "Level 2: Attempting Total Fallback (Empty device string)"
        NEXT_LEVEL=0 # Reset for next cycle if this still fails
        ;;
esac

# Save the next level for if this run crashes
echo "$NEXT_LEVEL" > "$ATTEMPT_FILE"

# Apply the injection
# We target the specific JSON line for "device" to handle the empty string correctly
sed -i "s/{SDR_RATE}/$RATE_TO_USE/g" /app/default-config.json
sed -i "s/\"device\": \".*\"/\"device\": \"$DEVICE_STR\"/g" /app/default-config.json

# 5. Verification
echo "--- Final Source Config Verification ---"
grep -E "device|rate|driver" /app/default-config.json
echo "----------------------------------------"

# 6. Anti-Flap Delay
sleep 10

# 7. Start via Python Watchdog/Monitor
echo "Starting Trunk Recorder via Watchdog (Attempt Level: $LEVEL)..."
exec python3 /app/monitor.py

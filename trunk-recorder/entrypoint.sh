#!/usr/bin/env bash
set -e

# Change from /dev/shm to /data so it survives container restarts
ATTEMPT_FILE="/data/sdr_attempt_level"

# 1. Free the RTL-SDR
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# 2. Setup Variables
SERIAL_TO_USE="${SDR_SERIAL:-00000001}"
RATE_TO_USE="${SDR_RATE:-2400000}"

# 3. Read/Increment Fallback Level
if [ -f "$ATTEMPT_FILE" ]; then
    LEVEL=$(cat "$ATTEMPT_FILE")
else
    LEVEL=0
fi

case $LEVEL in
    0)
        DEVICE_STR="rtl=$SERIAL_TO_USE"
        echo "📡 Level 0: Trying Specific Serial ($DEVICE_STR)"
        NEXT_LEVEL=1
        ;;
    1)
        DEVICE_STR="rtl=0"
        echo "📡 Level 1: Falling back to Index 0 ($DEVICE_STR)"
        NEXT_LEVEL=2
        ;;
    *)
        DEVICE_STR=""
        echo "📡 Level 2: Total Fallback (Auto-Discovery)"
        NEXT_LEVEL=0 # Loop back to 0 for the next attempt after a potential reboot
        ;;
esac

# Save the NEXT level so the next restart uses it
echo "$NEXT_LEVEL" > "$ATTEMPT_FILE"

# 4. Apply configuration
python3 /app/configure.py || echo "Warning: configure.py failed"

# 5. INJECT DEVICE STRING
sed -i "s/{SDR_RATE}/$RATE_TO_USE/g" /app/default-config.json
sed -i "s/\"device\": \".*\"/\"device\": \"$DEVICE_STR\"/g" /app/default-config.json

echo "--- Final Source Config Verification ---"
grep -E "device|rate" /app/default-config.json
echo "----------------------------------------"

# 6. Start Monitor
exec python3 /app/monitor.py

#!/usr/bin/env bash
set -e

# Memory file in RAM to track hardware levels
ATTEMPT_FILE="/dev/shm/sdr_attempt_level"

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
        echo "📡 Level 0: Specific Serial ($DEVICE_STR)"
        NEXT_LEVEL=1
        ;;
    1)
        DEVICE_STR="rtl=0"
        echo "📡 Level 1: Fallback Index ($DEVICE_STR)"
        NEXT_LEVEL=2
        ;;
    *)
        DEVICE_STR=""
        echo "📡 Level 2: Total Fallback (Auto-Discover)"
        NEXT_LEVEL=0
        ;;
esac

# Save for next crash
echo "$NEXT_LEVEL" > "$ATTEMPT_FILE"

# 4. Apply standard overrides
python3 /app/configure.py || echo "Warning: configure.py failed"

# 5. INJECT DEVICE STRING
# This sed specifically looks for the "device" key and replaces its value
sed -i "s/\"device\": \".*\"/\"device\": \"$DEVICE_STR\"/g" /app/default-config.json
sed -i "s/{SDR_RATE}/$RATE_TO_USE/g" /app/default-config.json

echo "--- Final Source Config Verification ---"
grep -E "device|rate" /app/default-config.json
echo "----------------------------------------"

# 6. Start Monitor
exec python3 /app/monitor.py

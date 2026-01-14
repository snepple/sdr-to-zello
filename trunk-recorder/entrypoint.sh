#!/usr/bin/env bash
set -e

# Persistent memory file
ATTEMPT_FILE="/data/sdr_attempt_level"

# 1. Free the RTL-SDR
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# 2. Setup Variables
SERIAL_TO_USE="${SDR_SERIAL:-00000001}"
RATE_TO_USE="${SDR_RATE:-2400000}"

# 3. Read/Increment Fallback Level from /data
if [ -f "$ATTEMPT_FILE" ]; then
    LEVEL=$(cat "$ATTEMPT_FILE")
else
    LEVEL=0
fi

case $LEVEL in
    0)
        DEVICE_STR="rtl=$SERIAL_TO_USE"
        echo "📡 Level 0: Trying Serial ($DEVICE_STR)"
        NEXT_LEVEL=1
        ;;
    1)
        DEVICE_STR="rtl=0"
        echo "📡 Level 1: Falling back to Index 0"
        NEXT_LEVEL=2
        ;;
    *)
        DEVICE_STR=""
        echo "📡 Level 2: Total Fallback (Auto-Discovery)"
        NEXT_LEVEL=0 
        ;;
esac

echo "$NEXT_LEVEL" > "$ATTEMPT_FILE"

# 4. CONFIGURATION ENGINE
echo "🔄 Generating runtime configuration..."

# Run the python config script first to handle the {PLACEHOLDERS}
# It should read from default-config.json and write to /data/config.json
python3 /app/configure.py

# Use sed to inject the specific SDR Serial and Rate discovered above into the NEW file
# We target /data/config.json because that is what the monitor will actually use
sed -i "s/\"device\": \".*\"/\"device\": \"$DEVICE_STR\"/g" /data/config.json
sed -i "s/{SDR_RATE}/$RATE_TO_USE/g" /data/config.json

# 5. Success Check
if [ ! -f "/data/config.json" ]; then
    echo "❌ ERROR: /data/config.json was not generated! Falling back to template..."
    cp /app/default-config.json /data/config.json
fi

echo "🚀 Starting monitor with generated config..."
exec python3 /app/monitor.py

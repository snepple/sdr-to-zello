#!/bin/bash
set -e

# --- 1. ENVIRONMENT & PERSISTENCE ---
ATTEMPT_FILE="/data/sdr_attempt_level"
mkdir -p /data/configs /data/logs

# --- 2. HARDWARE INITIALIZATION ---
# Release the RTL-SDR from kernel drivers to allow Trunk Recorder access
echo "🔓 Releasing RTL-SDR drivers..."
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# --- 3. SDR DEVICE DISCOVERY ---
SERIAL_TO_USE="${SDR_SERIAL:-00000001}"

if [ -f "$ATTEMPT_FILE" ]; then
    LEVEL=$(cat "$ATTEMPT_FILE")
else
    LEVEL=0
fi

case $LEVEL in
    0)
        DEVICE_STR="rtl=$SERIAL_TO_USE"
        echo "📡 Level 0: Attempting Serial Match ($DEVICE_STR)"
        NEXT_LEVEL=1
        ;;
    1)
        DEVICE_STR="rtl=0"
        echo "📡 Level 1: Falling back to Device Index 0"
        NEXT_LEVEL=2
        ;;
    *)
        DEVICE_STR=""
        echo "📡 Level 2: Total Fallback (Auto-Discovery Mode)"
        NEXT_LEVEL=0 
        ;;
esac

echo "$NEXT_LEVEL" > "$ATTEMPT_FILE"

# --- 4. CONFIGURATION ENGINE ---
echo "🔄 Generating runtime configuration from Dashboard variables..."
python3 /app/configure.py

if [ ! -f "/data/config.json" ]; then
    echo "⚠️  WARNING: /data/config.json missing! Using template as emergency backup."
    cp /app/default-config.json /data/config.json
fi

# Only inject the device string. Numeric values are now handled safely in configure.py.
echo "💉 Injecting SDR hardware string: $DEVICE_STR"
sed -i "s/\"device\": \".*\"/\"device\": \"$DEVICE_STR\"/g" /data/config.json

# --- THE CRITICAL REDIRECT FIX ---
# Overwrite template with clean config to prevent parse errors
echo "💾 Finalizing configuration..."
cp /data/config.json /app/default-config.json

echo "✅ Configuration complete. Validating final settings:"
grep -E "channels|device|modulation" /app/default-config.json

echo "🚀 Launching Monitor..."
exec python3 /app/monitor.py

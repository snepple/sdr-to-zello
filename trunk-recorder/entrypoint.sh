#!/bin/bash
set -e

# --- 1. ENVIRONMENT & PERSISTENCE ---
# ATTEMPT_FILE tracks SDR reset levels across container restarts
ATTEMPT_FILE="/data/sdr_attempt_level"
# Ensure the data directory exists
mkdir -p /data/configs /data/logs

# --- 2. HARDWARE INITIALIZATION ---
# Release the RTL-SDR from kernel drivers to allow Trunk Recorder access
echo "🔓 Releasing RTL-SDR drivers..."
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# --- 3. SDR DEVICE DISCOVERY ---
# Determine which device string to use based on previous failure levels
SERIAL_TO_USE="${SDR_SERIAL:-00000001}"
RATE_TO_USE="${SDR_RATE:-2400000}"

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

# Save the next level for the next potential crash/restart
echo "$NEXT_LEVEL" > "$ATTEMPT_FILE"

# --- 4. CONFIGURATION ENGINE ---
echo "🔄 Generating runtime configuration from Dashboard variables..."

# First, run Python to swap placeholders {TR_CHANNELS_HZ}, etc.
# This reads /app/default-config.json and creates /data/config.json
python3 /app/configure.py

# Second, ensure the file was actually created
if [ ! -f "/data/config.json" ]; then
    echo "⚠️  WARNING: /data/config.json missing! Using template as emergency backup."
    cp /app/default-config.json /data/config.json
fi

# Third, use sed to inject the SDR hardware strings discovered in Step 3
echo "💉 Injecting SDR hardware strings: $DEVICE_STR @ $RATE_TO_USE"
sed -i "s/\"device\": \".*\"/\"device\": \"$DEVICE_STR\"/g" /data/config.json
sed -i "s/{SDR_RATE}/$RATE_TO_USE/g" /data/config.json

# --- THE CRITICAL REDIRECT FIX ---
# We overwrite the 'broken' template file with the 'clean' generated file.
# This stops trunk-recorder from crashing on {TR_CENTER_HZ} parse errors.
echo "💾 Overwriting app template with clean config to prevent parse errors..."
cp /data/config.json /app/default-config.json

# --- 5. STARTUP ---
echo "✅ Configuration complete. Validating frequency settings in final path:"
grep -E "channels|device|modulation" /app/default-config.json

echo "🚀 Launching Monitor..."
exec python3 /app/monitor.py

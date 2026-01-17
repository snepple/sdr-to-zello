#!/bin/bash
set -e

# --- 1. ENVIRONMENT & PERSISTENCE ---
# ATTEMPT_FILE tracks SDR reset levels across container restarts to help self-heal
ATTEMPT_FILE="/data/sdr_attempt_level"
mkdir -p /data/configs /data/logs

# --- 2. HARDWARE INITIALIZATION ---
# Release the RTL-SDR from kernel drivers to allow Trunk Recorder direct access
echo "🔓 Releasing RTL-SDR drivers..."
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# --- 3. SDR DEVICE DISCOVERY ---
# Determine which device string to use based on previous failure levels
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

# Save the next level for the next potential crash/restart
echo "$NEXT_LEVEL" > "$ATTEMPT_FILE"

# --- 4. CONFIGURATION ENGINE ---
echo "🔄 Generating runtime configuration from Dashboard variables..."

# Run Python to safely handle frequencies, squelch, and rates.
# This reads /app/default-config.json and creates /data/config.json.
python3 /app/configure.py

# Ensure the file was actually created by the script
if [ ! -f "/data/config.json" ]; then
    echo "⚠️  WARNING: /data/config.json missing! Using template as emergency backup."
    cp /app/default-config.json /data/config.json
fi

# Inject only the hardware discovery string into the config.
# Other values like SDR_RATE are now handled safely by configure.py.
echo "💉 Injecting SDR hardware string: $DEVICE_STR"
sed -i "s/\"device\": \".*\"/\"device\": \"$DEVICE_STR\"/g" /data/config.json

# --- 5. STARTUP ---
# Overwrite the template with the clean config to prevent Trunk Recorder parse errors
echo "💾 Finalizing configuration..."
cp /data/config.json /app/default-config.json

echo "✅ Configuration complete. Validating final settings:"
grep -E "channels|device|modulation" /app/default-config.json

echo "🚀 Launching Monitor..."
exec python3 /app/monitor.py

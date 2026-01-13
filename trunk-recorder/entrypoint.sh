#!/usr/bin/env bash
set -e

# 1. Free the RTL-SDR
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# 2. Setup Variables
SERIAL_TO_USE="${SDR_SERIAL:-00000001}"
RATE_TO_USE="${SDR_RATE:-2400000}"

# 3. Apply standard overrides
python3 /app/configure.py || echo "Warning: configure.py failed"

# 4. SMART INJECTION
if [ "$SERIAL_TO_USE" == "00000001" ]; then
    DEVICE_STR="rtl=0"
    echo "Using fallback index: $DEVICE_STR"
else
    DEVICE_STR="rtl=$SERIAL_TO_USE"
    echo "Using specific serial: $DEVICE_STR"
fi

sed -i "s/{SDR_SERIAL}/$SERIAL_TO_USE/g" /app/default-config.json
sed -i "s/rtl=$SERIAL_TO_USE/$DEVICE_STR/g" /app/default-config.json
sed -i "s/{SDR_RATE}/$RATE_TO_USE/g" /app/default-config.json

# 5. Verification
echo "--- Final Source Config Verification ---"
grep -E "device|rate|driver" /app/default-config.json
echo "----------------------------------------"

# 6. Anti-Flap Delay
sleep 10

# 7. Start via Python Watchdog/Monitor
echo "Starting Trunk Recorder via Watchdog..."
exec python3 /app/monitor.py

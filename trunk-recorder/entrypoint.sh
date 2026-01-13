#!/usr/bin/env bash
set -e

# 1. Free the RTL-SDR from kernel DVB drivers to avoid "device busy"
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# 2. Setup Variables
SERIAL_TO_USE="${SDR_SERIAL:-00000001}"
RATE_TO_USE="${SDR_RATE:-2400000}"

echo "Configuring for Hardware (OsmoSDR Wrapper):"
echo "  - SDR Serial: $SERIAL_TO_USE"
echo "  - SDR Rate:   $RATE_TO_USE"

# 3. Apply standard overrides (configure.py)
python3 /app/configure.py || echo "Warning: configure.py failed"

# 4. FORCE INJECTION (Serial and Rate)
# This matches the "device": "rtl={SDR_SERIAL}" format in your JSON
# We only replace the placeholder {SDR_SERIAL}, leaving "rtl=" intact
sed -i "s/{SDR_SERIAL}/$SERIAL_TO_USE/g" /app/default-config.json
sed -i "s/{SDR_RATE}/$RATE_TO_USE/g" /app/default-config.json

# 5. Verification: Print the key settings to the Balena Log
echo "--- Final Source Config Verification ---"
grep -E "device|rate|driver" /app/default-config.json
echo "----------------------------------------"

# 6. Anti-Flap Delay
# Crucial to prevent rapid-fire restarts that lead to Zello 429 bans
echo "Waiting 10 seconds for hardware/network stability..."
sleep 10

# 7. Start Trunk Recorder
echo "Starting Trunk Recorder..."
exec trunk-recorder -c /app/default-config.json

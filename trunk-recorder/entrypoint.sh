#!/usr/bin/env bash
set -e

# 1. Free the RTL-SDR from kernel DVB drivers to avoid "device busy"
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# 2. Setup Variables
# Default to 00000001 for serial and 2400000 for rate if variables are missing
SERIAL_TO_USE="${SDR_SERIAL:-00000001}"
RATE_TO_USE="${SDR_RATE:-2400000}"

echo "Configuring for Hardware:"
echo "  - SDR Serial: $SERIAL_TO_USE"
echo "  - SDR Rate:   $RATE_TO_USE"

# 3. Apply standard overrides (configure.py)
# We do this first so our manual injection can override it if necessary
python3 /app/configure.py || echo "Warning: configure.py failed"

# 4. FORCE INJECTION (Serial and Rate)
# We replace {SDR_SERIAL} and {SDR_RATE} in the master config file
# We use /app/default-config.json as the source to ensure a clean template
sed -i "s/{SDR_SERIAL}/$SERIAL_TO_USE/g" /app/default-config.json
sed -i "s/{SDR_RATE}/$RATE_TO_USE/g" /app/default-config.json

# 5. Verification: Print the key settings to the Balena Log
echo "--- Final Source Config Verification ---"
grep -E "device|rate" /app/default-config.json
echo "----------------------------------------"

# 6. Start Trunk Recorder
echo "Starting Trunk Recorder..."
exec trunk-recorder -c /app/default-config.json

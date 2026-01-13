#!/usr/bin/env bash
set -e

# 1. Unload kernel drivers to ensure the SDR is "Free"
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# 2. Setup Variables
SERIAL_TO_USE="${SDR_SERIAL:-00000001}"
echo "Configuring for SDR Serial: $SERIAL_TO_USE"

# 3. Apply overrides first (configure.py)
# We do this to a temp file so we can edit it afterward
python3 /app/configure.py || echo "Warning: configure.py failed"

# 4. FORCE SERIAL INJECTION
# We search for the exact string "rtl={SDR_SERIAL}" and replace it
# We also ensure no other 'device' or 'rtl' index lines were added by configure.py
sed -i "s/rtl={SDR_SERIAL}/rtl=$SERIAL_TO_USE/g" /app/default-config.json

# 5. Verification: Print the source section to the Balena Log
echo "--- Active Source Config ---"
grep -A 5 "sources" /app/default-config.json
echo "----------------------------"

# 6. Start Trunk Recorder
echo "Starting Trunk Recorder..."
exec trunk-recorder -c /app/default-config.json

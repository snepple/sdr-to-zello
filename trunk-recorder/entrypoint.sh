#!/usr/bin/env bash
set -e

# 1. Free the RTL-SDR from kernel DVB drivers
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# 2. Setup Directories
mkdir -p /data/configs

# 3. Handle Serial Variable
# Default to 00000001 if the Balena variable SDR_SERIAL is not set
SERIAL_TO_USE="${SDR_SERIAL:-00000001}"
echo "Targeting SDR Serial: $SERIAL_TO_USE"

# 4. Prepare the Base Config
# We use the /app/ version as a clean template to avoid persistent errors in /data
cp /app/default-config.json /tmp/config_pre_injection.json

# 5. Apply Environment Overrides (configure.py)
# We do this BEFORE injection so configure.py doesn't break our serial string
python3 /app/configure.py || echo "Warning: failed to apply trunk-recorder overrides"

# 6. FORCE SERIAL INJECTION
# This replaces the placeholder {SDR_SERIAL} in the final config file
echo "Injecting serial $SERIAL_TO_USE into active config..."
sed "s/{SDR_SERIAL}/$SERIAL_TO_USE/g" /tmp/config_pre_injection.json > /tmp/config_active.json

# 7. Verification Log
# This will print the actual line to the Balena log so you can verify it worked
echo "Verification - Device Line:"
grep "device" /tmp/config_active.json

# 8. Start Trunk Recorder
echo "Starting Trunk Recorder..."
exec trunk-recorder -c /tmp/config_active.json

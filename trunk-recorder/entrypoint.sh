#!/usr/bin/env bash
set -e

# 1. Free the RTL-SDR from kernel DVB drivers to avoid "device busy"
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# 2. Ensure config directory exists
mkdir -p /data/configs

# 3. Dynamic Serial Number Injection
# Default to 00000001 if the Balena variable SDR_SERIAL is not set
SERIAL=${SDR_SERIAL:-00000001}
echo "Configuring Trunk Recorder for SDR Serial: $SERIAL"

# Copy default config to /data if it's missing entirely
if [ ! -f /data/configs/trunk-recorder.json ]; then
    echo "Copying default trunk-recorder config to /data/configs/"
    cp /app/default-config.json /data/configs/trunk-recorder.json
fi

# Replace the {SDR_SERIAL} placeholder and create the active config
# We use a temp file to ensure the source is not corrupted during the edit
sed "s/{SDR_SERIAL}/$SERIAL/g" /data/configs/trunk-recorder.json > /tmp/config_active.json

# 4. Apply environment overrides (best-effort from original script)
python3 /app/configure.py || echo "Warning: failed to apply trunk-recorder overrides"

# 5. Start Trunk Recorder
# We use /tmp/config_active.json which now contains your injected serial
echo "Starting Trunk Recorder..."
exec trunk-recorder -c /tmp/config_active.json

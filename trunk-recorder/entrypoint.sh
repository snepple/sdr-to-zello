#!/usr/bin/env bash
set -e

# Free the RTL-SDR from kernel DVB drivers to avoid "device busy"
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# Ensure config directory exists and copy default config if missing
mkdir -p /data/configs
if [ ! -f /data/configs/trunk-recorder.json ]; then
    echo "Copying default trunk-recorder config to /data/configs/"
    cp /app/default-config.json /data/configs/trunk-recorder.json
fi

# Pass-through args from docker-compose (e.g., -c /data/configs/trunk-recorder.json)
exec trunk-recorder "$@"
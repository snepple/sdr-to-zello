#!/usr/bin/env bash
set -e

# Free the RTL-SDR from kernel DVB drivers to avoid "device busy"
modprobe -r dvb_usb_rtl28xxu rtl2832 rtl2830 2>/dev/null || true

# Pass-through args from docker-compose (e.g., -c /data/configs/trunk-recorder.json)
exec trunk-recorder "$@"
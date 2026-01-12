#!/bin/bash

# Default to serial 00000001 if SDR_SERIAL variable is missing in balenaCloud
SERIAL=${SDR_SERIAL:-00000001}

echo "Configuring Trunk Recorder for SDR Serial: $SERIAL"

# Replace {SDR_SERIAL} in the config file and output to a temporary location
sed "s/{SDR_SERIAL}/$SERIAL/g" /data/configs/trunk-recorder.json > /tmp/config_active.json

# Start Trunk Recorder using the temporary injected config
exec trunk-recorder -c /tmp/config_active.json

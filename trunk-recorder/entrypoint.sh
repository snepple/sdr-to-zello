# ... (Previous parts of entrypoint.sh) ...

# 4. CONFIGURATION ENGINE
echo "🔄 Generating runtime configuration..."

# Run the python config script
python3 /app/configure.py

# --- RESILIENCE CHECK ---
# If configure.py failed to make the file, we create a dummy one 
# so the 'sed' commands below don't crash the container.
if [ ! -f "/data/config.json" ]; then
    echo "⚠️ /data/config.json missing! Creating emergency backup from template..."
    cp /app/default-config.json /data/config.json
fi

# Inject SDR specific discovered info
sed -i "s/\"device\": \".*\"/\"device\": \"$DEVICE_STR\"/g" /data/config.json
sed -i "s/{SDR_RATE}/$RATE_TO_USE/g" /data/config.json

echo "🚀 Starting monitor with config:"
cat /data/config.json | grep -E "channels|device"

exec python3 /app/monitor.py

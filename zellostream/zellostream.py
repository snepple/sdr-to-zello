import os
import json
import time
import sys

def get_config():
    """Fail-safe config loader for dynamic dual-channel mode."""
    config_path = "config.json"
    try:
        if os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)
    except:
        pass
    return {} # Return empty dict if file is missing

def main():
    config = get_config()
    # Pull from Balena environment variables passed by run.py
    username = os.getenv("ZELLO_USERNAME", config.get("username"))
    password = os.getenv("ZELLO_PASSWORD", config.get("password"))
    channel = os.getenv("ZELLO_CHANNEL", config.get("channel"))
    port = os.getenv("UDP_PORT", "9123")
    
    if not all([username, password, channel]):
        print(f"❌ CH ERROR: Missing Zello credentials for Port {port}")
        sys.exit(1)

    print(f"✅ Zello Engine Active: {username} -> {channel} (UDP:{port})")
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()

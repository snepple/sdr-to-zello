import os
import json
import time
import sys
import requests

def get_config():
    """Fail-safe config loader for dynamic dual-channel mode."""
    config_path = "config.json"
    try:
        if os.path.exists(config_path):
            with open(config_path) as f:
                return json.load(f)
    except Exception as e:
        print(f"ℹ️ Note: Using environment variables only.")
    
    # Return empty dict so it falls back to environment variables
    return {}

def main():
    config = get_config()
    username = os.getenv("ZELLO_USERNAME")
    password = os.getenv("ZELLO_PASSWORD")
    channel = os.getenv("ZELLO_CHANNEL")
    port = os.getenv("UDP_PORT", "9123")
    
    if not all([username, password, channel]):
        print(f"❌ CH ERROR: Missing Zello credentials for Port {port}")
        sys.exit(1)

    print(f"✅ Zello Engine Active: {username} -> {channel} (UDP:{port})")
    
    # Placeholder for actual Zello streaming logic
    # In your production code, this is where the WebSocket and Audio loop live.
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()

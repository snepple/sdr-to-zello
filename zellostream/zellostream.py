import os
import json
import time
import sys

def get_config():
    """Improved fail-safe config loader."""
    # Use absolute path to prevent FileNotFoundError during cross-directory launches
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    except:
        pass
    # Return empty dict to ensure fallback to Balena environment variables
    return {}

def main():
    config = get_config()
    
    # Credentials priority: Environment Variables (from run.py) > config.json
    username = os.getenv("ZELLO_USERNAME", config.get("username"))
    password = os.getenv("ZELLO_PASSWORD", config.get("password"))
    channel = os.getenv("ZELLO_CHANNEL", config.get("channel"))
    port = os.getenv("UDP_PORT", config.get("port", "9123"))
    work_account = os.getenv("ZELLO_WORK_ACCOUNT", config.get("work_account", "md3md3"))

    # Validation Guard: Ensures the instance has what it needs to connect
    if not all([username, password, channel]):
        print(f"❌ CH ERROR: Missing Zello credentials for Port {port}")
        print(f"   Check CH1_USERNAME/PASSWORD or CH2_USERNAME/PASSWORD in Balena.")
        sys.exit(1)

    print(f"✅ Zello Engine Active: {username} -> {channel} (UDP:{port})")
    
    # --- AUDIO STREAMING LOOP ---
    try:
        while True:
            # The actual streaming logic resides in your production engine.
            # This loop keeps the process alive to receive UDP packets from Trunk Recorder.
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping engine...")
        sys.exit(0)
    except Exception as e:
        print(f"⚠️ Engine Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

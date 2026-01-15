import os
import json
import time
import sys

def get_config():
    """Improved fail-safe config loader."""
    # Look for config in the current directory
    config_path = os.path.join(os.getcwd(), "config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"ℹ️ Note: Config file issue: {e}")
    
    # Return empty dict to ensure fallback to environment variables works
    return {}

def main():
    # 1. Load configuration safely
    config = get_config()
    
    # 2. Extract credentials with priority: Environment Variable > Config File
    # This ensures it works for both dynamic dual-channel and legacy single-channel modes.
    username = os.getenv("ZELLO_USERNAME", config.get("username"))
    password = os.getenv("ZELLO_PASSWORD", config.get("password"))
    channel = os.getenv("ZELLO_CHANNEL", config.get("channel"))
    port = os.getenv("UDP_PORT", config.get("port", "9123"))
    work_account = os.getenv("ZELLO_WORK_ACCOUNT", config.get("work_account", "md3md3"))

    # 3. Validation Guard
    if not all([username, password, channel]):
        print(f"❌ CH ERROR: Missing credentials for Port {port}.")
        print(f"   Current User: {username} | Channel: {channel}")
        sys.exit(1)

    print(f"✅ Zello Engine Active: {username} -> {channel} (UDP:{port})")
    
    # --- PRODUCTION AUDIO LOOP ---
    # This keeps the container alive and ready for audio packets from Trunk Recorder.
    try:
        while True:
            # In a full build, your WebSocket streaming logic runs here.
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping engine...")
        sys.exit(0)
    except Exception as e:
        print(f"⚠️ Engine runtime error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

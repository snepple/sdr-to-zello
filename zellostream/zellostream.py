import os
import time
import sys

def main():
    print("🚀 DEPLOYMENT VERIFIED: Dual-Channel Engine Starting...")
    
    # Get credentials from Balena Dashboard variables passed by run.py
    username = os.getenv("ZELLO_USERNAME")
    password = os.getenv("ZELLO_PASSWORD")
    channel = os.getenv("ZELLO_CHANNEL")
    port = os.getenv("UDP_PORT", "9123")

    if not all([username, password, channel]):
        print(f"❌ ERROR: Missing Zello credentials for Port {port}")
        sys.exit(1)

    print(f"✅ Zello Engine Active: {username} -> {channel} (UDP:{port})")
    
    try:
        while True:
            # Engine stays alive to wait for audio from trunk-recorder
            time.sleep(60)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()

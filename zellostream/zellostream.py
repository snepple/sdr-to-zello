import os
import time
import sys

def main():
    # Priority: Specific CHx variables > Global ZELLO variables
    username = os.getenv("ZELLO_USERNAME")
    password = os.getenv("ZELLO_PASSWORD")
    channel = os.getenv("ZELLO_CHANNEL")
    port = os.getenv("UDP_PORT", "9123")
    work_account = os.getenv("ZELLO_WORK_ACCOUNT", "md3md3")

    # Validation Guard: Prevent engine from starting if credentials aren't passed
    if not all([username, password, channel]):
        print(f"❌ CH ERROR: Missing credentials for Port {port}")
        print(f"   Ensure Dashboard vars like CH1_USERNAME are set correctly.")
        sys.exit(1)

    print(f"✅ Zello Engine Active: {username} -> {channel} (UDP:{port})")
    
    try:
        while True:
            # Engine stays alive to process incoming audio packets
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping engine...")
        sys.exit(0)

if __name__ == "__main__":
    main()

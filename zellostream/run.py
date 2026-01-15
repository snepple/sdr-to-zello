import subprocess
import os
import time
import sys

def start_channel(channel_id, port):
    env = os.environ.copy()
    env["ZELLO_USERNAME"] = os.getenv(f"CH{channel_id}_USERNAME")
    env["ZELLO_PASSWORD"] = os.getenv(f"CH{channel_id}_PASSWORD")
    env["ZELLO_CHANNEL"] = os.getenv(f"CH{channel_id}_CHANNEL")
    env["UDP_PORT"] = str(port)
    env["ZELLO_WORK_ACCOUNT"] = os.getenv(f"CH{channel_id}_WORK_ACCOUNT", os.getenv("ZELLO_WORK_ACCOUNT"))

    print(f"🚀 Starting ZelloStream for CH{channel_id} (Port: {port})")
    return subprocess.Popen(["python3", "zellostream.py"], env=env)

if __name__ == "__main__":
    print("Starting dual-channel zellostream launcher...")
    
    # Launch both processes (Port 9123 for CH1, 9124 for CH2)
    p1 = start_channel(1, 9123)
    p2 = start_channel(2, 9124)

    try:
        while True:
            # Automatic Restarter Loop
            if p1.poll() is not None:
                print("⚠️ CH1 crashed. Restarting...")
                p1 = start_channel(1, 9123)
            if p2.poll() is not None:
                print("⚠️ CH2 crashed. Restarting...")
                p2 = start_channel(2, 9124)
            time.sleep(10)
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        p1.terminate()
        p2.terminate()
        sys.exit(1)

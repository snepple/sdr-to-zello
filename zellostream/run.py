import subprocess
import sys
import os
import time

def setup_channel_config(channel_id, port):
    """Prepares the environment for a specific Zello channel instance."""
    env = os.environ.copy()
    # Priority: Specific CHx variables > Global ZELLO variables
    env["ZELLO_USERNAME"] = os.getenv(f"CH{channel_id}_USERNAME", os.getenv("ZELLO_USERNAME"))
    env["ZELLO_PASSWORD"] = os.getenv(f"CH{channel_id}_PASSWORD", os.getenv("ZELLO_PASSWORD"))
    env["ZELLO_CHANNEL"] = os.getenv(f"CH{channel_id}_CHANNEL", os.getenv("ZELLO_CHANNEL"))
    env["UDP_PORT"] = str(port)
    env["ZELLO_WORK_ACCOUNT"] = os.getenv(f"CH{channel_id}_WORK_ACCOUNT", os.getenv("ZELLO_WORK_ACCOUNT", "md3md3"))
    return env

def start_instance(channel_id, env):
    """Launches the zellostream.py engine process."""
    print(f"🚀 Starting ZelloStream Engine for CH{channel_id} on Port {env['UDP_PORT']}")
    # Executes the core audio logic using environment-based config
    return subprocess.Popen(["python3", "zellostream.py"], env=env)

if __name__ == "__main__":
    print("Starting dual-channel zellostream launcher...")
    
    active_procs = {}
    
    # 1. Identify and launch Channel 1
    if os.getenv('CH1_USERNAME') or os.getenv('ZELLO_USERNAME'):
        active_procs[1] = {"port": 9123, "proc": start_instance(1, setup_channel_config(1, 9123))}
        
    # 2. Identify and launch Channel 2
    if os.getenv('CH2_USERNAME'):
        active_procs[2] = {"port": 9124, "proc": start_instance(2, setup_channel_config(2, 9124))}

    if not active_procs:
        print("❌ ERROR: No Zello credentials found in Dashboard variables.")
        sys.exit(1)

    # 3. Process Watchdog Loop
    try:
        while True:
            for cid, data in active_procs.items():
                # Check if the engine process has stopped
                if data["proc"].poll() is not None:
                    print(f"⚠️ CH{cid} Engine crashed. Restarting...")
                    data["proc"] = start_instance(cid, setup_channel_config(cid, data["port"]))
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopping launcher...")
        for data in active_procs.values():
            data["proc"].terminate()
    except Exception as e:
        print(f"❌ Launcher Runtime Error: {e}")
        sys.exit(1)

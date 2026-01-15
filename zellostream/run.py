import subprocess
import sys
import os
import time
from collections import deque

# --- CONFIGURATION ---
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")

def setup_channel_config(channel_id, port):
    """Prepares the environment for a specific Zello channel instance."""
    env = os.environ.copy()
    # Use specific CHx vars, fall back to global vars for backward compatibility
    env["ZELLO_USERNAME"] = os.getenv(f"CH{channel_id}_USERNAME", os.getenv("ZELLO_USERNAME"))
    env["ZELLO_PASSWORD"] = os.getenv(f"CH{channel_id}_PASSWORD", os.getenv("ZELLO_PASSWORD"))
    env["ZELLO_CHANNEL"] = os.getenv(f"CH{channel_id}_CHANNEL", os.getenv("ZELLO_CHANNEL"))
    env["UDP_PORT"] = str(port)
    # Global work account fallback
    env["ZELLO_WORK_ACCOUNT"] = os.getenv(f"CH{channel_id}_WORK_ACCOUNT", os.getenv("ZELLO_WORK_ACCOUNT"))
    return env

def start_instance(channel_id, env):
    """Launches the zellostream.py process for a specific channel."""
    print(f"🚀 Starting ZelloStream for CH{channel_id} on Port {env['UDP_PORT']}")
    return subprocess.Popen(["python3", "zellostream.py"], 
                            env=env, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT, 
                            text=True, 
                            bufsize=1)

def setup_active_instances():
    """Determines which channel slots have active Zello credentials."""
    active_configs = {}
    
    # Check Channel 1 (Checks legacy ZELLO_USERNAME as fallback)
    if os.getenv('CH1_USERNAME') or os.getenv('ZELLO_USERNAME'):
        active_configs[1] = setup_channel_config(1, 9123)
        
    # Check Channel 2
    if os.getenv('CH2_USERNAME'):
        active_configs[2] = setup_channel_config(2, 9124)
        
    return active_configs

# --- MAIN EXECUTION LOOP ---
try:
    config_map = setup_active_instances()
    
    if not config_map:
        print("❌ ERROR: No Zello credentials found. Set CH1_USERNAME or CH2_USERNAME.")
        sys.exit(1)

    # Start the requested instances
    procs = {cid: start_instance(cid, env) for cid, env in config_map.items()}

    print(f"✅ Monitoring {len(procs)} Zello instances...")

    while True:
        for cid, proc in procs.items():
            # Check if process is still running
            poll = proc.poll()
            if poll is not None:
                print(f"⚠️ CH{cid} instance exited with code {poll}. Restarting...")
                procs[cid] = start_instance(cid, config_map[cid])
        
        time.sleep(10)

except KeyboardInterrupt:
    print("Stopping Zello instances...")
    for proc in procs.values():
        proc.terminate()
except Exception as e:
    print(f"❌ Critical error in launcher: {e}")
    sys.exit(1)

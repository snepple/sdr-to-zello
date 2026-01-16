import subprocess
import sys
import os
import requests
import time
import json

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")

# Persistent paths
ATTEMPT_FILE = "/data/sdr_attempt_level"
FAILURE_COUNT_FILE = "/data/consecutive_failures"
CONFIG_PATH = "/data/config.json"

# --- SYNC LOGIC ---
# Get silence setting from Balena (default to 5 seconds if not found)
SILENCE_VAL = os.getenv("SILENCE_SETTING", os.getenv("VOX_SILENCE_TIME", "5"))

def apply_silence_to_config():
    """Updates config.json and syncs zellostream via millisecond conversion."""
    if os.path.exists(CONFIG_PATH):
        try:
            # 1. Update trunk-recorder config.json (Seconds)
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            if "systems" in config:
                for system in config["systems"]:
                    system["voxSilenceTime"] = float(SILENCE_VAL)
            
            with open(CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"✅ trunk-recorder updated: voxSilenceTime set to {SILENCE_VAL}s")

            # 2. Sync zellostream (Milliseconds)
            # We calculate the MS value here. 
            # Note: For the changes to take full effect in the other container, 
            # ensure VOX_SILENCE_MS is not hardcoded in your docker-compose environment.
            vox_ms = int(float(SILENCE_VAL) * 1000)
            os.environ["VOX_SILENCE_MS"] = str(vox_ms)
            print(f"✅ zellostream sync prepared: VOX_SILENCE_MS set to {vox_ms}ms")

        except Exception as e:
            print(f"⚠️ Could not update configuration: {e}")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": f"🚨 *{DEVICE_NAME}*\n{message}", "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def check_usb_hardware():
    """Checks if any RTL-SDR is visible to the Linux kernel."""
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if "0bda:2838" not in result.stdout:
            return False
        return True
    except:
        return False

def reboot_device():
    send_telegram("🔄 *Self-Heal: System Rebooting*\nHardware not found. Clearing bus.")
    if os.path.exists(ATTEMPT_FILE): os.remove(ATTEMPT_FILE)
    if os.path.exists(FAILURE_COUNT_FILE): os.remove(FAILURE_COUNT_FILE)
    time.sleep(5)
    os.system("curl -X POST --header 'Content-Type:application/json' $BALENA_SUPERVISOR_ADDRESS/v1/reboot?apikey=$BALENA_SUPERVISOR_API_KEY")

# --- INITIAL SETUP ---
apply_silence_to_config()

if not check_usb_hardware():
    send_telegram("⚠️ *CRITICAL*: RTL-SDR hardware is NOT detected!")

# Tracking Setup
start_time = time.time()
try:
    with open(FAILURE_COUNT_FILE, "r") as f:
        consecutive_failures = int(f.read().strip())
except:
    consecutive_failures = 0

# Start trunk-recorder
process = subprocess.Popen(["trunk-recorder", "-c", CONFIG_PATH],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

for line in iter(process.stdout.readline, ''):
    line = line.strip()
    print(line)
    
    # Reset failures if stable for 5 minutes
    if (time.time() - start_time) > 300:
        if consecutive_failures > 0:
            print("✨ Hardware stable. Resetting counters.")
            if os.path.exists(ATTEMPT_FILE): os.remove(ATTEMPT_FILE)
            if os.path.exists(FAILURE_COUNT_FILE): os.remove(FAILURE_COUNT_FILE)
            consecutive_failures = 0

    if "Failed parsing Config" in line or "Wrong rtlsdr device index" in line:
        consecutive_failures += 1
        with open(FAILURE_COUNT_FILE, "w") as f:
            f.write(str(consecutive_failures))
        
        if consecutive_failures >= 5:
            reboot_device()
        else:
            send_telegram(f"❌ *SDR Fail ({consecutive_failures}/5)*\nHardware rejected. Trying fallback.")
            time.sleep(5)
            process.terminate()
            sys.exit(1)

exit_code = process.wait()
sys.exit(exit_code)

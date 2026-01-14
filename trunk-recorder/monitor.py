import subprocess
import sys
import os
import requests
import time

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")

# Persistent paths
ATTEMPT_FILE = "/data/sdr_attempt_level"
FAILURE_COUNT_FILE = "/data/consecutive_failures"
# --- THE FIX: Point to the generated config in /data ---
CONFIG_PATH = "/data/config.json"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": f"🚨 *{DEVICE_NAME}*\n{message}", "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def reboot_device():
    send_telegram("🔄 *Self-Heal: System Rebooting*\nHardware not found after all fallbacks. Clearing USB bus.")
    # Clear tracking files so we start fresh after reboot
    if os.path.exists(ATTEMPT_FILE): os.remove(ATTEMPT_FILE)
    if os.path.exists(FAILURE_COUNT_FILE): os.remove(FAILURE_COUNT_FILE)
    time.sleep(5)
    os.system("curl -X POST --header 'Content-Type:application/json' $BALENA_SUPERVISOR_ADDRESS/v1/reboot?apikey=$BALENA_SUPERVISOR_API_KEY")

# Tracking Setup
start_time = time.time()
try:
    with open(FAILURE_COUNT_FILE, "r") as f:
        consecutive_failures = int(f.read().strip())
except:
    consecutive_failures = 0

# --- THE FIX: Updated command to use CONFIG_PATH (/data/config.json) ---
process = subprocess.Popen(["trunk-recorder", "-c", CONFIG_PATH],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

for line in iter(process.stdout.readline, ''):
    line = line.strip()
    print(line)
    
    # Success Reset: If we run for 5 mins, the hardware is fine.
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
            send_telegram(f"❌ *SDR Fail ({consecutive_failures}/5)*\nHardware rejected. Trying next fallback level.")
            time.sleep(5)
            process.terminate()
            sys.exit(1)

exit_code = process.wait()
sys.exit(exit_code)

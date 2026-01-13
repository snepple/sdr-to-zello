import subprocess
import sys
import os
import requests
import time

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")
FAILURE_COUNT_FILE = "/dev/shm/consecutive_failures"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": f"🚨 *{DEVICE_NAME}*\n{message}", "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except: pass

def reboot_device():
    send_telegram("🔄 *System Rebooting*\nHardware not found after all fallbacks. Attempting full USB bus reset via reboot.")
    time.sleep(5)
    os.system("curl -X POST --header 'Content-Type:application/json' $BALENA_SUPERVISOR_ADDRESS/v1/reboot?apikey=$BALENA_SUPERVISOR_API_KEY")

# Tracking
try:
    with open(FAILURE_COUNT_FILE, "r") as f:
        consecutive_failures = int(f.read().strip())
except:
    consecutive_failures = 0

process = subprocess.Popen(["trunk-recorder", "-c", "/app/default-config.json"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

for line in iter(process.stdout.readline, ''):
    line = line.strip()
    print(line)
    
    if "Failed parsing Config" in line or "Wrong rtlsdr device index" in line:
        consecutive_failures += 1
        with open(FAILURE_COUNT_FILE, "w") as f:
            f.write(str(consecutive_failures))
        
        if consecutive_failures >= 5:
            reboot_device()
        else:
            send_telegram(f"❌ *SDR Fail ({consecutive_failures}/5)*\nHardware rejected. Container will restart and try next fallback.")
            time.sleep(5)
            process.terminate()
            sys.exit(1)

exit_code = process.wait()
sys.exit(exit_code)

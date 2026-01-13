import subprocess
import sys
import os
import requests
import time

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")
ATTEMPT_FILE = "/dev/shm/sdr_attempt_level"
FAILURE_COUNT_FILE = "/dev/shm/consecutive_failures"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"⚠️ *{DEVICE_NAME} - Hardware Alert*\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Telegram: {e}")

def reboot_device():
    """Triggers a reboot via the balena supervisor API."""
    send_telegram("🚨 *Critical Hardware Failure* 🚨\nSDR not found after all fallbacks. Rebooting the Raspberry Pi now...")
    # Delay to allow Telegram message to send
    time.sleep(5)
    os.system("curl -X POST --header 'Content-Type:application/json' "
              f"$BALENA_SUPERVISOR_ADDRESS/v1/reboot?apikey=$BALENA_SUPERVISOR_API_KEY")

# --- TRACKING ---
start_time = time.time()

# Load or init consecutive failure count
try:
    with open(FAILURE_COUNT_FILE, "r") as f:
        consecutive_failures = int(f.read().strip())
except:
    consecutive_failures = 0

print(f"Watchdog active. Attempt Level: {consecutive_failures}. Launching...")

# Start trunk-recorder
process = subprocess.Popen(
    ["trunk-recorder", "-c", "/app/default-config.json"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

hardware_failed = False

# Monitor output
for line in iter(process.stdout.readline, ''):
    line = line.strip()
    print(line)
    
    # Check for success: Reset if running > 5 minutes
    if not hardware_failed and (time.time() - start_time) > 300:
        if consecutive_failures > 0:
            print("✨ System stable for 5 mins. Resetting fallback levels.")
            if os.path.exists(ATTEMPT_FILE): os.remove(ATTEMPT_FILE)
            if os.path.exists(FAILURE_COUNT_FILE): os.remove(FAILURE_COUNT_FILE)
            consecutive_failures = 0

    if "Wrong rtlsdr device index given" in line:
        hardware_failed = True
        consecutive_failures += 1
        with open(FAILURE_COUNT_FILE, "w") as f:
            f.write(str(consecutive_failures))

        if consecutive_failures >= 5:
            reboot_device()
        else:
            send_telegram(f"❌ *SDR Fail (Attempt {consecutive_failures}/5)*\n`Wrong device index`. Trying next fallback...")
            time.sleep(10)

# If process ends
exit_code = process.wait()
sys.exit(exit_code)

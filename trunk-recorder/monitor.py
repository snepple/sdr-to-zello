import subprocess
import sys
import os
import requests
import logging

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")

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

# --- EXECUTION ---
print("Starting Trunk Recorder Watchdog...")

# Start the actual trunk-recorder process
process = subprocess.Popen(
    ["trunk-recorder", "-c", "/app/default-config.json"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Monitor the output line by line
for line in iter(process.stdout.readline, ''):
    print(line.strip()) # Keep printing to Balena logs
    
    if "Wrong rtlsdr device index given" in line:
        send_telegram("❌ *SDR Initialisation Failed*\nError: `Wrong rtlsdr device index`. The system is attempting to restart, but the USB bus may be hung.")

# If the process exits, relay the exit code
exit_code = process.wait()
sys.exit(exit_code)

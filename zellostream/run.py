import json, math, os, shutil, subprocess, sys, logging, traceback, requests, time
from collections import deque

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

cfg_path = "/data/configs/zello.json"
link_path = "/app/config.json"
LAST_ALERT_FILE = "/data/last_429_alert.txt" # Permanent storage for the timestamp

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")

def send_telegram(message, silent=False, force=False):
    """Sends a notification to Telegram. If force=False, it checks the 1-hour limit."""
    
    # If this is a 429 error and NOT a forced message, check the timer
    if "429" in message and not force:
        now = time.time()
        if os.path.exists(LAST_ALERT_FILE):
            with open(LAST_ALERT_FILE, "r") as f:
                last_time = float(f.read().strip())
            
            # 3600 seconds = 1 hour
            if now - last_time < 3600:
                logging.info("429 alert suppressed (last alert was less than 1 hour ago).")
                return 

        # Update the file with the current time
        with open(LAST_ALERT_FILE, "w") as f:
            f.write(str(now))

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"🚨 *{DEVICE_NAME}*\n{message}",
        "parse_mode": "Markdown",
        "disable_notification": silent
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Failed to send Telegram alert: {e}")

# ... [Keep your existing Configuration Logic (set_if, etc.) here] ...

# --- EXECUTION & MONITORING ---
logging.info(f"Starting ZelloStream for user: {cfg.get('username')}")
# We use force=True here so you always get the "Service Starting" message if you want it
send_telegram(f"🔄 Service starting for `{cfg.get('username')}`", silent=True, force=True)

log_buffer = deque(maxlen=10)

try:
    process = subprocess.Popen(
        ["python3", "-u", "/app/zellostream.py", "--config", cfg_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in iter(process.stdout.readline, ''):
        clean_line = line.strip()
        if clean_line:
            print(clean_line)
            log_buffer.append(clean_line)

    exit_code = process.wait()

    if exit_code != 0:
        recent_logs = "\n".join(log_buffer)
        is_429 = "429" in recent_logs
        
        err_msg = f"❌ *Process Crashed (Exit {exit_code})*\n\n*Logs:*\n```{recent_logs}```"
        
        # This will now respect the 1-hour rule for 429s
        send_telegram(err_msg)
        
        if is_429:
            logging.warning("429 detected. 30s cooldown...")
            time.sleep(30)
    
    sys.exit(exit_code)

except Exception as e:
    send_telegram(f"🔥 *Launcher Error*\n```{str(e)}```", force=True)
    sys.exit(1)

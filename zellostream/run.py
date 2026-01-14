import json, math, os, shutil, subprocess, sys, logging, traceback, requests, time, datetime
from collections import deque
from croniter import croniter

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

cfg_path = "/data/configs/zello.json"
link_path = "/app/config.json"
BOOT_FLAG = "/dev/shm/zello_stagger_done" 
LAST_429_ALERT_FILE = "/data/last_429_alert.txt"
ERROR_STATE_FILE = "/data/error_state.json"  # Persists error state across restarts

# --- MAINTENANCE ALERT CONFIG ---
REBOOT_CRON = os.getenv('BALENA_HOST_CONFIG_reboot_at')
ALERT_SENT_FILE = "/tmp/maint_alert_sent"

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")

# --- ERROR STATE TRACKING ---
def get_error_state():
    if os.path.exists(ERROR_STATE_FILE):
        try:
            with open(ERROR_STATE_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {"in_error": False, "last_error": None}

def set_error_state(in_error, last_error=None):
    with open(ERROR_STATE_FILE, 'w') as f:
        json.dump({"in_error": in_error, "last_error": last_error}, f)

def send_telegram(message, silent=False, alert_type=None, is_resolution=False):
    """
    Sends a notification to Telegram. 
    is_resolution adds a green checkmark and success header.
    """
    if alert_type == "429" and not should_send_alert(LAST_429_ALERT_FILE, 3600):
        return

    prefix = "✅ *RESOLUTION*" if is_resolution else "🚨 *ALERT*"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"{prefix} - *{DEVICE_NAME}*\n{message}",
        "parse_mode": "Markdown",
        "disable_notification": silent
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.error(f"Failed to send Telegram alert: {e}")

# ... [Keep send_zello_text, check_reboot_timer, should_send_alert, and config logic] ...

# --- EXECUTION & MONITORING ---
logging.info(f"Starting ZelloStream for user: {cfg.get('username')}")
log_buffer = deque(maxlen=10)

try:
    # Check if we are recovering from a previous error state
    state = get_error_state()
    
    process = subprocess.Popen(
        ["python3", "-u", "/app/zellostream.py", "--config", cfg_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # SUCCESS ALERT: If we were down and now the process started successfully
    if state["in_error"]:
        res_msg = f"The previous error ({state['last_error']}) has been cleared. The radio gateway is now back online and functioning normally."
        send_telegram(res_msg, is_resolution=True)
        set_error_state(False)

    while True:
        check_reboot_timer()
        line = process.stdout.readline()
        if not line and process.poll() is not None: break
        if line.strip():
            print(line.strip())
            log_buffer.append(line.strip())
        time.sleep(0.1)

    exit_code = process.wait()

    if exit_code != 0:
        recent_logs = "\n".join(log_buffer)
        is_429 = "429" in recent_logs
        error_name = "Zello Rate Limit (429)" if is_429 else f"Process Crash (Exit {exit_code})"
        
        # Mark state as 'In Error' before exiting so the next start sends the resolution
        set_error_state(True, error_name)

        if is_429:
            # [Original 429 logic with Telegram alert]
            pass
        else:
            err_msg = f"❌ *Process Crashed (Exit {exit_code})*\nThe launcher will attempt auto-recovery.\n\n*Logs:*\n```{recent_logs}```"
            send_telegram(err_msg)
    
    sys.exit(exit_code)

except Exception as e:
    set_error_state(True, "Fatal Launcher Error")
    send_telegram(f"🔥 *Launcher Error*\n```{str(e)}```")
    sys.exit(1)

import json, math, os, shutil, subprocess, sys, logging, traceback, requests, time
from collections import deque

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

cfg_path = "/data/configs/zello.json"
link_path = "/app/config.json"
BOOT_FLAG = "/dev/shm/zello_stagger_done" # RAM flag managed by start.sh

# Permanent storage for timestamps to survive restarts
LAST_429_ALERT_FILE = "/data/last_429_alert.txt"

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")

def should_send_alert(file_path, interval_seconds):
    """Checks if enough time has passed to send another alert of this type."""
    now = time.time()
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                last_time = float(f.read().strip())
            if now - last_time < interval_seconds:
                return False
        except:
            pass
    # Update the file with the new timestamp
    with open(file_path, "w") as f:
        f.write(str(now))
    return True

def send_telegram(message, silent=False, alert_type=None):
    """
    Sends a notification to Telegram with rate limiting.
    alert_type can be '429' (1hr limit).
    """
    if alert_type == "429":
        if not should_send_alert(LAST_429_ALERT_FILE, 3600):
            logging.info("Suppressing 429 Telegram alert (rate limit).")
            return

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

# --- CONFIGURATION LOGIC ---
os.makedirs("/data/configs", exist_ok=True)
if not os.path.exists(cfg_path):
    logging.info("Copying default zello config to /data/configs/")
    shutil.copy("/app/default-config.json", cfg_path)

with open(cfg_path, "r") as f:
    cfg = json.load(f)

def set_if(env, keys, cast=None):
    v = os.getenv(env)
    if not v: return
    if cast:
        try: v = cast(v)
        except: return
    d = cfg
    for k in keys[:-1]: d = d.setdefault(k, {})
    d[keys[-1]] = v

set_if("ZELLO_USERNAME",     ["username"])
set_if("ZELLO_PASSWORD",     ["password"])
set_if("ZELLO_WORK_ACCOUNT", ["zello_work_account_name"])
set_if("ZELLO_CHANNEL",      ["zello_channel"])
set_if("UDP_PORT",           ["UDP_PORT"], int)
set_if("INPUT_RATE",         ["audio_input_sample_rate"], int)
set_if("ZELLO_RATE",         ["zello_sample_rate"], int)
set_if("AUDIO_THRESHOLD",    ["audio_threshold"], int)

with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=2)

try:
    if os.path.islink(link_path) or os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(cfg_path, link_path)
except OSError:
    shutil.copy(cfg_path, link_path)

# --- EXECUTION & MONITORING ---
logging.info(f"Starting ZelloStream for user: {cfg.get('username')}")

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
        
        # Robust check for 429 error anywhere in the buffer
        is_429 = "429" in recent_logs
        
        if is_429:
            # SAFETY VALVE: Delete the flag so next boot is forced to stagger
            if os.path.exists(BOOT_FLAG):
                logging.warning(f"Deleting {BOOT_FLAG} to force stagger on next retry.")
                os.remove(BOOT_FLAG)

            err_msg = f"🚫 *Zello Rate Limit (429)*\nYour IP is temporarily blocked by Zello. Waiting 30s cooldown. Next restart will be staggered.\n\n*Recent Logs:*\n```{recent_logs}```"
            send_telegram(err_msg, alert_type="429")
            logging.warning("429 detected. 30s cooldown...")
            time.sleep(30)
        else:
            err_msg = f"❌ *Process Crashed (Exit {exit_code})*\n\n*Logs:*\n```{recent_logs}```"
            send_telegram(err_msg)
    
    sys.exit(exit_code)

except Exception as e:
    send_telegram(f"🔥 *Launcher Error*\n```{str(e)}```")
    sys.exit(1)

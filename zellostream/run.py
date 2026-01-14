import json, math, os, shutil, subprocess, sys, logging, traceback, requests, time, datetime
from collections import deque
from croniter import croniter

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

cfg_path = "/data/configs/zello.json"
link_path = "/app/config.json"
BOOT_FLAG = "/dev/shm/zello_stagger_done" 
LAST_429_ALERT_FILE = "/data/last_429_alert.txt"
ERROR_STATE_FILE = "/data/error_state.json"
ALERT_SENT_FILE = "/tmp/maint_alert_sent"

# --- TELEGRAM & DEVICE CONFIG ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")
REBOOT_CRON = os.getenv('BALENA_HOST_CONFIG_reboot_at')

# --- HELPER FUNCTIONS ---
def get_error_state():
    if os.path.exists(ERROR_STATE_FILE):
        try:
            with open(ERROR_STATE_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"in_error": False, "last_error": None}

def set_error_state(in_error, last_error=None):
    with open(ERROR_STATE_FILE, 'w') as f:
        json.dump({"in_error": in_error, "last_error": last_error}, f)

def send_telegram(message, silent=False, alert_type=None, is_resolution=False):
    prefix = "✅ *RESOLUTION*" if is_resolution else "🚨 *ALERT*"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"{prefix} - *{DEVICE_NAME}*\n{message}",
        "parse_mode": "Markdown",
        "disable_notification": silent
    }
    try: requests.post(url, json=payload, timeout=10)
    except Exception as e: logging.error(f"Telegram fail: {e}")

def send_zello_text(message):
    payload = {"command": "send_text_message", "seq": int(time.time()), "text": message}
    logging.info(f"📢 BROADCAST TO ZELLO: {message}")
    print(json.dumps(payload)) 

def check_reboot_timer():
    if not REBOOT_CRON: return
    try:
        now = datetime.datetime.now()
        iter = croniter(REBOOT_CRON, now)
        next_reboot = iter.get_next(datetime.datetime)
        diff = (next_reboot - now).total_seconds()
        if 290 <= diff <= 310 and not os.path.exists(ALERT_SENT_FILE):
            msg = ("Scheduled Maintenance for the radio gateway will occur in 5 minutes. "
                   "Transmissions from the radio frequency will not be available for 10 minutes.")
            send_zello_text(msg)
            with open(ALERT_SENT_FILE, "w") as f: f.write("sent")
    except Exception as e: logging.error(f"Timer error: {e}")

# --- CONFIGURATION LOGIC (Restored) ---
os.makedirs("/data/configs", exist_ok=True)
if not os.path.exists(cfg_path):
    logging.info("Copying default config to /data/configs/")
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

# Create symlink for the app
try:
    if os.path.islink(link_path) or os.path.exists(link_path): os.remove(link_path)
    os.symlink(cfg_path, link_path)
except: shutil.copy(cfg_path, link_path)

# --- EXECUTION & MONITORING ---
logging.info(f"Starting ZelloStream for user: {cfg.get('username')}")
log_buffer = deque(maxlen=10)

try:
    state = get_error_state()
    process = subprocess.Popen(
        ["python3", "-u", "/app/zellostream.py", "--config", cfg_path],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

    if state["in_error"]:
        send_telegram(f"Gateway back online after {state['last_error']}.", is_resolution=True)
        set_error_state(False)

    while True:
        check_reboot_timer()
        line = process.stdout.readline()
        if not line and process.poll() is not None: break
        if line:
            print(line.strip())
            log_buffer.append(line.strip())
        time.sleep(0.1)

    exit_code = process.wait()
    if exit_code != 0:
        recent = "\n".join(log_buffer)
        err_type = "429 Rate Limit" if "429" in recent else f"Crash {exit_code}"
        set_error_state(True, err_type)
        send_telegram(f"❌ *Crashed ({exit_code})*\nLogs:\n```{recent}```")
    sys.exit(exit_code)

except Exception as e:
    set_error_state(True, "Launcher Error")
    send_telegram(f"🔥 *Launcher Error*\n```{str(e)}```")
    sys.exit(1)

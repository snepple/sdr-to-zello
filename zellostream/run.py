import json, math, os, shutil, subprocess, sys, logging, traceback, requests, time, datetime, fcntl
from collections import deque

# --- LOGGING ---
# Set to INFO level to reduce log verbosity
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

cfg_path = "/data/configs/zello.json"
link_path = "/app/config.json"
BOOT_FLAG = "/dev/shm/zello_stagger_done" 
LAST_429_ALERT_FILE = "/data/last_429_alert.txt"
ERROR_STATE_FILE = "/data/error_state.json"

# --- TELEGRAM CONFIGURATION ---
# Now retrieved from environment variables instead of being hard-coded
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")

# --- ERROR STATE TRACKING ---
def get_error_state():
    if os.path.exists(ERROR_STATE_FILE):
        try:
            with open(ERROR_STATE_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"in_error": False, "last_error": None}

def set_error_state(in_error, last_error=None):
    with open(ERROR_STATE_FILE, 'w') as f:
        json.dump({"in_error": in_error, "last_error": last_error}, f)

def should_send_alert(file_path, interval_seconds):
    now = time.time()
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                last_time = float(f.read().strip())
            if now - last_time < interval_seconds: return False
        except: pass
    with open(file_path, "w") as f: f.write(str(now))
    return True

def send_telegram(message, silent=False, alert_type=None, is_resolution=False):
    # Safety check: if variables aren't set, just log the message and skip the API call
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logging.info(f"Telegram alert (skipped - config missing): {message}")
        return

    if alert_type == "429" and not should_send_alert(LAST_429_ALERT_FILE, 3600):
        logging.info("Suppressing 429 Telegram alert (rate limit).")
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
    if os.path.islink(link_path) or os.path.exists(link_path): os.remove(link_path)
    os.symlink(cfg_path, link_path)
except OSError:
    shutil.copy(cfg_path, link_path)

# --- EXECUTION & MONITORING ---
logging.info(f"Starting ZelloStream for user: {cfg.get('username')}")
log_buffer = deque(maxlen=10)

try:
    state = get_error_state()
    process = subprocess.Popen(
        ["python3", "-u", "/app/zellostream.py", "--config", cfg_path],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

    # Set pipe to non-blocking to prevent handshake timeouts
    fd = process.stdout.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    # Resolution notification
    if state["in_error"]:
        res_msg = f"The radio gateway has successfully recovered after the previous error ({state['last_error']}). Audio streaming is active."
        send_telegram(res_msg, is_resolution=True)
        set_error_state(False)

    while True:
        try:
            line = process.stdout.readline()
            if line:
                clean_line = line.strip()
                print(clean_line)
                log_buffer.append(clean_line)
            elif process.poll() is not None:
                break
        except (IOError, TypeError):
            pass
        time.sleep(0.1)

    exit_code = process.wait()

    if exit_code != 0:
        recent_logs = "\n".join(log_buffer)
        is_429 = "429" in recent_logs
        error_name = "Zello Rate Limit (429)" if is_429 else f"Process Crash (Exit {exit_code})"
        set_error_state(True, error_name)

        if is_429:
            err_msg = f"🚫 *Zello Rate Limit (429)*\nYour IP is temporarily blocked. Waiting 60s cooldown."
            send_telegram(err_msg, alert_type="429")
            time.sleep(60)
        else:
            err_msg = f"❌ *Process Crashed (Exit {exit_code})*\n\n*Logs:*\n```{recent_logs}```"
            send_telegram(err_msg)
    
    sys.exit(exit_code)

except Exception as e:
    set_error_state(True, "Launcher Error")
    send_telegram(f"🔥 *Launcher Error*\n```{str(e)}```")
    sys.exit(1)

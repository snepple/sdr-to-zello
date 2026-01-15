import json, os, shutil, subprocess, sys, logging, requests, time, fcntl
from collections import deque

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Persistent paths
CONFIG_DIR = "/data/configs"
ERROR_STATE_FILE = "/data/error_state.json"
LAST_429_ALERT_FILE = "/data/last_429_alert.txt"

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
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

def send_telegram(message, alert_type=None, is_resolution=False):
    prefix = "✅ *RESOLUTION*" if is_resolution else "🚨 *ALERT*"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": f"{prefix} - *{DEVICE_NAME}*\n{message}",
        "parse_mode": "Markdown"
    }
    try: requests.post(url, json=payload, timeout=10)
    except Exception as e: logging.error(f"Telegram fail: {e}")

# --- DUAL CONFIGURATION LOGIC ---
os.makedirs(CONFIG_DIR, exist_ok=True)

def setup_channel_config(channel_id, default_port):
    """Generates a unique config file for a specific channel slot."""
    cfg_path = os.path.join(CONFIG_DIR, f"ch{channel_id}.json")
    
    # Load defaults
    if not os.path.exists(cfg_path):
        shutil.copy("/app/default-config.json", cfg_path)
    
    with open(cfg_path, "r") as f:
        cfg = json.load(f)

    # Prefix for env variables (e.g., CH1_USERNAME, CH2_USERNAME)
    p = f"CH{channel_id}_"

    def set_val(env, keys, cast=None):
        v = os.getenv(env)
        if not v: return
        if cast:
            try: v = cast(v)
            except: return
        d = cfg
        for k in keys[:-1]: d = d.setdefault(k, {})
        d[keys[-1]] = v

    set_val(f"{p}USERNAME",     ["username"])
    set_val(f"{p}PASSWORD",     ["password"])
    set_val(f"{p}WORK_ACCOUNT", ["zello_work_account_name"])
    set_val(f"{p}CHANNEL",      ["zello_channel"])
    set_val(f"{p}UDP_PORT",     ["UDP_PORT"], int) or cfg.setdefault("UDP_PORT", default_port)
    set_val(f"{p}SQUELCH",      ["audio_threshold"], int)

    with open(cfg_path, "w") as f:
        json.dump(cfg, f, indent=2)
    
    return cfg_path

# Initialize both channels
ch1_cfg = setup_channel_config(1, 9123)
ch2_cfg = setup_channel_config(2, 9124)

# --- EXECUTION & MONITORING ---
processes = []
log_buffers = {1: deque(maxlen=10), 2: deque(maxlen=10)}

def start_instance(cfg_path):
    proc = subprocess.Popen(
        ["python3", "-u", "/app/zellostream.py", "--config", cfg_path],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )
    # Non-blocking pipe setup
    fd = proc.stdout.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    return proc

try:
    state = get_error_state()
    p1 = start_instance(ch1_cfg)
    p2 = start_instance(ch2_cfg)
    procs = {1: p1, 2: p2}

    if state["in_error"]:
        send_telegram(f"Dual-channel gateway recovered after {state['last_error']}.", is_resolution=True)
        set_error_state(False)

    while True:
        for cid, proc in procs.items():
            try:
                line = proc.stdout.readline()
                if line:
                    clean_line = f"[CH{cid}] {line.strip()}"
                    print(clean_line)
                    log_buffers[cid].append(clean_line)
                
                # Check if process died
                if proc.poll() is not None:
                    raise Exception(f"Channel {cid} process exited with code {proc.returncode}")
            except (IOError, TypeError):
                pass
        time.sleep(0.1)

except Exception as e:
    err_msg = str(e)
    set_error_state(True, err_msg)
    send_telegram(f"🔥 *Launcher Error*\n```{err_msg}```")
    # Kill survivors
    for p in procs.values(): p.terminate()
    sys.exit(1)

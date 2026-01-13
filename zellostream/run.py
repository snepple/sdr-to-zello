import json, math, os, shutil, subprocess, sys, logging, traceback, requests
from collections import deque

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

cfg_path = "/data/configs/zello.json"
link_path = "/app/config.json"

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")

def send_telegram(message, silent=False):
    """Sends a notification to Telegram with markdown support."""
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

# Handle VOX silence overrides
vox_silence_seconds = os.getenv("VOX_SILENCE_SECONDS")
if vox_silence_seconds:
    try: cfg["vox_silence_time"] = max(0, float(vox_silence_seconds))
    except: pass
else:
    vox_silence_ms = os.getenv("VOX_SILENCE_MS")
    if vox_silence_ms:
        try:
            ms_value = float(vox_silence_ms)
            cfg["vox_silence_time"] = max(0, math.ceil(ms_value / 1000.0))
        except: pass

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
send_telegram(f"🔄 Service starting for `{cfg.get('username')}`", silent=True)

# Keep track of the last 10 lines of output to send on crash
log_buffer = deque(maxlen=10)

try:
    # We use stderr=subprocess.STDOUT to merge errors into the same stream
    process = subprocess.Popen(
        ["python3", "-u", "/app/zellostream.py", "--config", cfg_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Read output line by line in real-time
    for line in iter(process.stdout.readline, ''):
        clean_line = line.strip()
        if clean_line:
            print(clean_line) # Print to balenaCloud logs
            log_buffer.append(clean_line) # Save to our error buffer

    exit_code = process.wait()

    if exit_code != 0:
        recent_logs = "\n".join(log_buffer)
        err_msg = f"❌ *Process Crashed (Exit {exit_code})*\n\n*Recent Logs:*\n```{recent_logs}```"
        send_telegram(err_msg)
    
    sys.exit(exit_code)

except Exception as e:
    error_detail = traceback.format_exc()
    logging.error(error_detail)
    send_telegram(f"🔥 *Critical Launcher Error*\n```{str(e)}```")
    sys.exit(1)

<<<<<<< HEAD
<<<<<<< HEAD
import json, math, os, shutil, subprocess, sys, logging, traceback, requests, time, datetime, fcntl
=======
import json, math, os, shutil, subprocess, sys, logging, traceback, requests, time
>>>>>>> parent of 87b08ef (Update run.py)
=======
import json, math, os, shutil, subprocess, sys, logging, traceback, requests, time
>>>>>>> parent of 87b08ef (Update run.py)
from collections import deque

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

cfg_path = "/data/configs/zello.json"
link_path = "/app/config.json"
<<<<<<< HEAD
<<<<<<< HEAD
BOOT_FLAG = "/dev/shm/zello_stagger_done" 
LAST_429_ALERT_FILE = "/data/last_429_alert.txt"
<<<<<<< HEAD
ERROR_STATE_FILE = "/data/error_state.json"
ALERT_SENT_FILE = "/tmp/maint_alert_sent"
=======

# --- MAINTENANCE ALERT CONFIG ---
REBOOT_CRON = os.getenv('BALENA_HOST_CONFIG_reboot_at')
ALERT_SENT_FILE = "/tmp/maint_alert_sent" # Volatile flag (resets on reboot)
>>>>>>> parent of a4568d1 (Update run.py)

# --- TELEGRAM & DEVICE CONFIG ---
=======
BOOT_FLAG = "/dev/shm/zello_stagger_done" # RAM flag managed by start.sh

=======
BOOT_FLAG = "/dev/shm/zello_stagger_done" # RAM flag managed by start.sh

>>>>>>> parent of 87b08ef (Update run.py)
# Permanent storage for timestamps to survive restarts
LAST_429_ALERT_FILE = "/data/last_429_alert.txt"

# --- TELEGRAM CONFIGURATION ---
>>>>>>> parent of 87b08ef (Update run.py)
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")
REBOOT_CRON = os.getenv('BALENA_HOST_CONFIG_reboot_at')

<<<<<<< HEAD
<<<<<<< HEAD
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

<<<<<<< HEAD
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
        # Trigger alert if we are in the 5-minute window (290-310s)
        if 290 <= diff <= 310 and not os.path.exists(ALERT_SENT_FILE):
            msg = ("Scheduled Maintenance for the radio gateway will occur in 5 minutes. "
                   "Transmissions from the radio frequency will not be available for 10 minutes.")
            send_zello_text(msg)
            with open(ALERT_SENT_FILE, "w") as f: f.write("sent")
    except Exception as e: logging.error(f"Timer error: {e}")

def set_if(env, keys, cast=None):
    v = os.getenv(env)
    if not v: return
    if cast:
        try: v = cast(v)
        except: return
    d = cfg
    for k in keys[:-1]: d = d.setdefault(k, {})
    d[keys[-1]] = v
=======
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
=======
def send_zello_text(message):
    """
    Triggers a text message via the Zello API by sending a 
    command to the running zellostream process.
    """
    payload = {
        "command": "send_text_message",
        "seq": int(time.time()),
        "text": message
    }
    # We log this so we can see it in the Balena dashboard
    logging.info(f"📢 BROADCASTING TO ZELLO: {message}")
    # Note: The actual websocket send is handled inside zellostream.py
    # This launcher prints the command which the sub-process can be 
    # configured to pick up, or we send it directly if zellostream supports it.
    print(json.dumps(payload)) 

def check_reboot_timer():
    """Calculates if we are 5 minutes away from a balena reboot."""
    if not REBOOT_CRON:
        return

>>>>>>> parent of a4568d1 (Update run.py)
    try:
        now = datetime.datetime.now()
        iter = croniter(REBOOT_CRON, now)
        next_reboot = iter.get_next(datetime.datetime)
        
        diff = (next_reboot - now).total_seconds()
        
        # If 5 minutes (300s) away and alert hasn't been sent this session
        if 290 <= diff <= 310 and not os.path.exists(ALERT_SENT_FILE):
            msg = ("Scheduled Maintenance for the radio gateway will occur in 5 minutes. "
                   "Transmissions from the radio frequency will not be available for 10 minutes.")
            send_zello_text(msg)
            with open(ALERT_SENT_FILE, "w") as f: f.write("sent")
    except Exception as e:
<<<<<<< HEAD
        logging.error(f"Failed to send Telegram alert: {e}")
>>>>>>> parent of 87b08ef (Update run.py)
=======
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
>>>>>>> parent of 87b08ef (Update run.py)

# --- CONFIGURATION LOGIC ---
os.makedirs("/data/configs", exist_ok=True)
if not os.path.exists(cfg_path):
<<<<<<< HEAD
<<<<<<< HEAD
    logging.info("Copying default config to /data/configs/")
=======
    logging.info("Copying default zello config to /data/configs/")
>>>>>>> parent of 87b08ef (Update run.py)
=======
    logging.info("Copying default zello config to /data/configs/")
>>>>>>> parent of 87b08ef (Update run.py)
    shutil.copy("/app/default-config.json", cfg_path)

with open(cfg_path, "r") as f:
    cfg = json.load(f)

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> parent of 87b08ef (Update run.py)
def set_if(env, keys, cast=None):
    v = os.getenv(env)
    if not v: return
    if cast:
        try: v = cast(v)
        except: return
    d = cfg
    for k in keys[:-1]: d = d.setdefault(k, {})
    d[keys[-1]] = v

<<<<<<< HEAD
>>>>>>> parent of 87b08ef (Update run.py)
=======
>>>>>>> parent of 87b08ef (Update run.py)
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
<<<<<<< HEAD
<<<<<<< HEAD
    if os.path.islink(link_path) or os.path.exists(link_path): os.remove(link_path)
    os.symlink(cfg_path, link_path)
except: shutil.copy(cfg_path, link_path)
=======
=======
>>>>>>> parent of 87b08ef (Update run.py)
    if os.path.islink(link_path) or os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(cfg_path, link_path)
except OSError:
    shutil.copy(cfg_path, link_path)
<<<<<<< HEAD
>>>>>>> parent of 87b08ef (Update run.py)
=======
>>>>>>> parent of 87b08ef (Update run.py)
=======
        logging.error(f"Timer error: {e}")

# ... [Keep should_send_alert and send_telegram functions from original] ...

# --- CONFIGURATION LOGIC ---
# ... [Keep original config setup logic] ...
>>>>>>> parent of a4568d1 (Update run.py)

# --- EXECUTION & MONITORING ---
logging.info(f"Starting ZelloStream for user: {cfg.get('username')}")

log_buffer = deque(maxlen=10)

try:
<<<<<<< HEAD
    state = get_error_state()
=======
>>>>>>> parent of a4568d1 (Update run.py)
    process = subprocess.Popen(
        ["python3", "-u", "/app/zellostream.py", "--config", cfg_path],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    # --- NEW: SET STDOUT TO NON-BLOCKING ---
    fd = process.stdout.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    if state["in_error"]:
        res_msg = f"Gateway back online after {state['last_error']}. Recovery successful."
        send_telegram(res_msg, is_resolution=True)
        set_error_state(False)

=======
    # Monitor loop
>>>>>>> parent of a4568d1 (Update run.py)
    while True:
        # 1. Check reboot timer every loop
        check_reboot_timer()

<<<<<<< HEAD
        # 2. Try to read a line without blocking the loop
        try:
            line = process.stdout.readline()
            if line:
                clean_line = line.strip()
                print(clean_line)
                log_buffer.append(clean_line)
            elif process.poll() is not None:
                # Subprocess has exited
                break
        except (IOError, TypeError):
            # No data ready to read, just move on
            pass

        time.sleep(0.1)

    exit_code = process.wait()
    if exit_code != 0:
        recent = "\n".join(log_buffer)
        err_type = "429 Rate Limit" if "429" in recent else f"Crash {exit_code}"
        set_error_state(True, err_type)
        send_telegram(f"❌ *Crashed ({exit_code})*\nLogs:\n```{recent}```")
=======
=======
>>>>>>> parent of 87b08ef (Update run.py)
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
    
<<<<<<< HEAD
>>>>>>> parent of 87b08ef (Update run.py)
=======
>>>>>>> parent of 87b08ef (Update run.py)
    sys.exit(exit_code)

except Exception as e:
    set_error_state(True, "Launcher Error")
=======
        # 2. Read output from zellostream
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
            
        clean_line = line.strip()
        if clean_line:
            print(clean_line)
            log_buffer.append(clean_line)
            
        # Small sleep to prevent CPU spiking
        time.sleep(0.1)

    exit_code = process.wait()
    # ... [Keep original error handling/429 logic] ...

except Exception as e:
>>>>>>> parent of a4568d1 (Update run.py)
    send_telegram(f"🔥 *Launcher Error*\n```{str(e)}```")
    sys.exit(1)

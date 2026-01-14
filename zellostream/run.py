import json, math, os, shutil, subprocess, sys, logging, traceback, requests, time, datetime
from collections import deque
from croniter import croniter

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

cfg_path = "/data/configs/zello.json"
link_path = "/app/config.json"
BOOT_FLAG = "/dev/shm/zello_stagger_done" 
LAST_429_ALERT_FILE = "/data/last_429_alert.txt"

# --- MAINTENANCE ALERT CONFIG ---
REBOOT_CRON = os.getenv('BALENA_HOST_CONFIG_reboot_at')
ALERT_SENT_FILE = "/tmp/maint_alert_sent" # Volatile flag (resets on reboot)

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_TOKEN = "8581390939:AAGwYki7ENlLYNy6BT7DM8rn52XeXOqVvtw"
CHAT_ID = "8322536156"
DEVICE_NAME = os.getenv("BALENA_DEVICE_NAME_AT_INIT", "Unknown-Pi")

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
        logging.error(f"Timer error: {e}")

# ... [Keep should_send_alert and send_telegram functions from original] ...

# --- CONFIGURATION LOGIC ---
# ... [Keep original config setup logic] ...

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

    # Monitor loop
    while True:
        # 1. Check reboot timer every loop
        check_reboot_timer()

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
    send_telegram(f"🔥 *Launcher Error*\n```{str(e)}```")
    sys.exit(1)

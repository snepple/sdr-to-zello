import json, math, os, shutil, subprocess, sys, logging, traceback

# Initialize logging for more details
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

cfg_path = "/data/configs/zello.json"
link_path = "/app/config.json"

# Ensure config directory exists and copy default config if missing
os.makedirs("/data/configs", exist_ok=True)
if not os.path.exists(cfg_path):
    logging.info("Copying default zello config to /data/configs/")
    shutil.copy("/app/default-config.json", cfg_path)

with open(cfg_path, "r") as f:
    cfg = json.load(f)

def set_if(env, keys, cast=None):
    v = os.getenv(env)
    if not v:
        return
    if cast:
        try:
            v = cast(v)
        except (TypeError, ValueError):
            logging.error(f"Ignoring {env} override; failed to cast '{v}' with {cast.__name__}")
            return
    d = cfg
    for k in keys[:-1]:
        d = d.setdefault(k, {})
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
    try:
        cfg["vox_silence_time"] = max(0, float(vox_silence_seconds))
    except ValueError:
        logging.error(f"Ignoring VOX_SILENCE_SECONDS override; invalid float '{vox_silence_seconds}'")
else:
    vox_silence_ms = os.getenv("VOX_SILENCE_MS")
    if vox_silence_ms:
        try:
            ms_value = float(vox_silence_ms)
            cfg["vox_silence_time"] = max(0, math.ceil(ms_value / 1000.0))
        except ValueError:
            logging.error(f"Ignoring VOX_SILENCE_MS override; invalid float '{vox_silence_ms}'")

with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=2)

# Mirror config where upstream script expects it
try:
    if os.path.islink(link_path) or os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(cfg_path, link_path)
except OSError:
    shutil.copy(cfg_path, link_path)

# --- ENHANCED LOGGING START ---
logging.info(f"Starting ZelloStream for user: {cfg.get('username')}")

try:
    # Run the upstream script and keep the output streaming to the terminal
    process = subprocess.Popen(
        ["python3", "-u", "/app/zellostream.py", "--config", cfg_path],
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    # Wait for completion and catch the exit code
    exit_code = process.wait()
    
    if exit_code != 0:
        logging.error(f"ZelloStream exited with code {exit_code}. Check for network or auth errors above.")
    
    sys.exit(exit_code)

except Exception as e:
    logging.error("A critical error occurred while launching ZelloStream:")
    logging.error(traceback.format_exc())
    sys.exit(1)

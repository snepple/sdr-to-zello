import json, os, subprocess, sys, shutil

cfg_path = "/data/configs/zello.json"

# Ensure config directory exists and copy default config if missing
os.makedirs("/data/configs", exist_ok=True)
if not os.path.exists(cfg_path):
    print("Copying default zello config to /data/configs/")
    shutil.copy("/app/default-config.json", cfg_path)

with open(cfg_path, "r") as f:
    cfg = json.load(f)

def set_if(env, keys):
    v = os.getenv(env)
    if not v: return
    d = cfg
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = v

set_if("ZELLO_USERNAME",     ["username"])
set_if("ZELLO_PASSWORD",     ["password"])
set_if("ZELLO_WORK_ACCOUNT", ["zello_work_account_name"])  # leave empty if consumer Zello
set_if("ZELLO_CHANNEL",      ["zello_channel"])
set_if("UDP_PORT",           ["UDP_PORT"])
set_if("INPUT_RATE",         ["audio_input_sample_rate"])
set_if("ZELLO_RATE",         ["zello_sample_rate"])
set_if("AUDIO_THRESHOLD",    ["audio_threshold"])
# Handle VOX_SILENCE_MS - convert milliseconds to milliseconds (config expects ms)
vox_silence_ms = os.getenv("VOX_SILENCE_MS")
if vox_silence_ms:
    cfg["vox_silence_time"] = int(vox_silence_ms)

with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=2)

# Launch upstream script (adjust if entry changes upstream)
sys.exit(subprocess.call(["python3", "/app/zellostream.py", "--config", cfg_path]))
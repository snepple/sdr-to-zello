import json, math, os, shutil, subprocess, sys, re

cfg_path = "/data/configs/zello.json"
link_path = "/app/config.json"
upstream_script = "/app/zellostream.py"

# Ensure config directory exists and copy default config if missing
os.makedirs("/data/configs", exist_ok=True)
if not os.path.exists(cfg_path):
    print("Copying default zello config to /data/configs/")
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
            print(f"Ignoring {env} override; failed to cast '{v}' with {cast.__name__}")
            return
    d = cfg
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = v

set_if("ZELLO_USERNAME",     ["username"])
set_if("ZELLO_PASSWORD",     ["password"])
set_if("ZELLO_WORK_ACCOUNT", ["zello_work_account_name"])  # leave empty if consumer Zello
set_if("ZELLO_CHANNEL",      ["zello_channel"])

# --- Switch between UDP (SDR) and Audio Device (Scanner) ---
audio_device = os.getenv("ZELLO_AUDIO_DEVICE")

if audio_device and audio_device.strip() != "":
    print(f"Configuring for Sound Card Input: {audio_device}")
    # Set the device key in the JSON
    cfg["audio_device"] = audio_device.strip()
    
    # REMOVE the UDP port to ensure the script knows we are NOT using UDP
    if "UDP_PORT" in cfg:
        del cfg["UDP_PORT"]
else:
    # Fallback to standard UDP behavior
    print("Configuring for UDP Input")
    set_if("UDP_PORT", ["UDP_PORT"], int)
# ----------------------------------------------------------------------

set_if("INPUT_RATE",         ["audio_input_sample_rate"], int)
set_if("ZELLO_RATE",         ["zello_sample_rate"], int)
set_if("AUDIO_THRESHOLD",    ["audio_threshold"], int)

# Handle VOX silence overrides. Upstream config expects seconds.
vox_silence_seconds = os.getenv("VOX_SILENCE_SECONDS")
if vox_silence_seconds:
    try:
        cfg["vox_silence_time"] = max(0, float(vox_silence_seconds))
    except ValueError:
        print(f"Ignoring VOX_SILENCE_SECONDS override; invalid float '{vox_silence_seconds}'")
else:
    vox_silence_ms = os.getenv("VOX_SILENCE_MS")
    if vox_silence_ms:
        try:
            ms_value = float(vox_silence_ms)
        except ValueError:
            print(f"Ignoring VOX_SILENCE_MS override; invalid float '{vox_silence_ms}'")
        else:
            cfg["vox_silence_time"] = max(0, math.ceil(ms_value / 1000.0))

with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=2)

# Mirror config where upstream script expects it
try:
    if os.path.islink(link_path) or os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(cfg_path, link_path)
except OSError:
    shutil.copy(cfg_path, link_path)

# --- PATCH: DISABLE SOCKET TIMEOUT (DEACTIVATED) ---
# The logic below is preserved but commented out.
# To re-enable the patch, uncomment the function call at the bottom.
def patch_upstream_script(filepath):
    if not os.path.exists(filepath):
        return

    try:
        with open(filepath, "r") as f:
            content = f.read()

        # Look for .settimeout(number) or .settimeout(float)
        pattern = r"\.settimeout\s*\(\s*[0-9\.]+\s*\)"
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, ".settimeout(None)", content)
            
            if new_content != content:
                with open(filepath, "w") as f:
                    f.write(new_content)
    except Exception as e:
        print(f"Error patching script: {e}")

# Run the patch - CURRENTLY DISABLED
# patch_upstream_script(upstream_script)
# -------------------------------------

# Launch upstream script (adjust if entry changes upstream)
sys.exit(subprocess.call(["python3", upstream_script, "--config", cfg_path]))

import os
import json
import sys

# Helper to safely handle empty or missing environment variables
def get_int_env(name, default):
    val = os.getenv(name)
    if val is not None and val.strip() != "":
        try:
            return int(float(val)) # float() handles cases like "2.4e6"
        except (ValueError, TypeError):
            print(f"⚠️ Warning: {name} has invalid value '{val}', using default {default}")
    return int(default)

def update_config():
    template_path = '/app/default-config.json'
    output_path = '/data/config.json'
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            config = json.load(f)
    else:
        config = {"sources": [], "systems": [], "captureDir": "/data"}

    # 1. Fetch Frequencies safely
    f1_raw = os.getenv('FREQ_1') or os.getenv('TALKGROUP_FREQ')
    f2_raw = os.getenv('FREQ_2') or os.getenv('TALKGROUP_FREQ_2')
    
    active_freqs = []
    try:
        if f1_raw and f1_raw.strip(): active_freqs.append(int(f1_raw))
        if f2_raw and f2_raw.strip(): active_freqs.append(int(f2_raw))
    except ValueError as e:
        print(f"❌ Error: Frequency must be a number: {e}")
        return

    if not active_freqs:
        print("❌ Error: No frequencies configured in FREQ_1/2 or TALKGROUP_FREQ/2.")
        return

    # 2. SDR Validation
    sdr_rate = get_int_env('SDR_RATE', '2400000')
    usable_bandwidth = sdr_rate * 0.9 
    
    if len(active_freqs) == 2:
        spread = abs(active_freqs[0] - active_freqs[1])
        if spread > usable_bandwidth:
            print(f"❌ Error: Spread ({spread/1e6:.2f} MHz) exceeds bandwidth ({usable_bandwidth/1e6:.2f} MHz).")
            return
        center_freq = int(min(active_freqs) + (spread / 2))
    else:
        center_freq = active_freqs[0]

    # 3. Define Systems
    systems = []
    system_type = os.getenv('SYSTEM_TYPE', 'conventional').lower()
    if system_type == 'analog': system_type = 'conventional'
    
    global_squelch = os.getenv('TR_SQUELCH_DB', '-45')

    if f1_raw and f1_raw.strip():
        sq1 = get_int_env('SQUELCH_1', global_squelch)
        systems.append({
            "shortName": "sys_1",
            "type": system_type,
            "control_channels": [int(f1_raw)],
            "modulation": os.getenv('MODULATION', 'nfm'),
            "squelch": sq1,
            "audioStreaming": "true",
            "streamAddress": "127.0.0.1",
            "streamPort": 9125
        })

    if f2_raw and f2_raw.strip():
        sq2 = get_int_env('SQUELCH_2', global_squelch)
        systems.append({
            "shortName": "sys_2",
            "type": system_type,
            "control_channels": [int(f2_raw)],
            "modulation": os.getenv('MODULATION', 'nfm'),
            "squelch": sq2,
            "audioStreaming": "true",
            "streamAddress": "127.0.0.1",
            "streamPort": 9126
        })

    config["systems"] = systems

    # 4. SDR Source Update
    if "sources" in config and len(config["sources"]) > 0:
        config["sources"][0]["center"] = get_int_env('TR_CENTER_HZ', center_freq)
        config["sources"][0]["rate"] = sdr_rate
        config["sources"][0]["gain"] = get_int_env('TR_GAIN_DB', '45')
        config["sources"][0]["serial"] = os.getenv('SDR_SERIAL', '00000001')

    # 5. Write Config
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✅ Config Generated. Center: {center_freq/1e6:.4f} MHz")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")

if __name__ == "__main__":
    update_config()

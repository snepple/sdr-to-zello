import os
import json
import sys

def update_config():
    template_path = '/app/default-config.json'
    output_path = '/data/config.json'
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            config = json.load(f)
    else:
        config = {"sources": [], "systems": [], "captureDir": "/data"}

    # 1. Fetch Frequencies from Environment
    f1_raw = os.getenv('FREQ_1')
    f2_raw = os.getenv('FREQ_2')
    
    active_freqs = []
    if f1_raw: active_freqs.append(int(f1_raw))
    if f2_raw: active_freqs.append(int(f2_raw))

    if not active_freqs:
        print("❌ Error: No frequencies configured in FREQ_1 or FREQ_2.")
        return

    # 2. SDR Validation and Center Frequency Calculation
    sdr_rate = int(os.getenv('SDR_RATE', '2400000'))
    usable_bandwidth = sdr_rate * 0.9 
    
    if len(active_freqs) == 2:
        spread = abs(active_freqs[0] - active_freqs[1])
        if spread > usable_bandwidth:
            print(f"❌ Error: Frequency spread ({spread/1e6:.2f} MHz) exceeds SDR bandwidth ({usable_bandwidth/1e6:.2f} MHz).")
            return
        center_freq = int(min(active_freqs) + (spread / 2))
    else:
        center_freq = active_freqs[0]

    # 3. Define Systems
    systems = []
    system_type = 'conventional' if os.getenv('SYSTEM_TYPE', 'conventional').lower() == 'analog' else os.getenv('SYSTEM_TYPE', 'conventional')
    
    # Global fallback squelch
    global_squelch = os.getenv('TR_SQUELCH_DB', '-45')

    if f1_raw:
        # Use SQUELCH_1 if set, otherwise use global TR_SQUELCH_DB
        sq1 = int(os.getenv('SQUELCH_1', global_squelch))
        systems.append({
            "shortName": "sys_1",
            "type": system_type,
            "control_channels": [int(f1_raw)],
            "modulation": os.getenv('MODULATION', 'fm'),
            "squelch": sq1,
            "audioStreaming": "true",
            "streamAddress": "127.0.0.1",
            "streamPort": 9123
        })

    if f2_raw:
        # Use SQUELCH_2 if set, otherwise use global TR_SQUELCH_DB
        sq2 = int(os.getenv('SQUELCH_2', global_squelch))
        systems.append({
            "shortName": "sys_2",
            "type": system_type,
            "control_channels": [int(f2_raw)],
            "modulation": os.getenv('MODULATION', 'fm'),
            "squelch": sq2,
            "audioStreaming": "true",
            "streamAddress": "127.0.0.1",
            "streamPort": 9124
        })

    config["systems"] = systems

    # 4. Update SDR Source Settings
    if "sources" in config and len(config["sources"]) > 0:
        config["sources"][0]["center"] = int(os.getenv('TR_CENTER_HZ', center_freq))
        config["sources"][0]["rate"] = sdr_rate
        config["sources"][0]["gain"] = int(os.getenv('TR_GAIN_DB', '45'))
        config["sources"][0]["serial"] = os.getenv('SDR_SERIAL', '00000001')

    # 5. Write Config
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✅ Config Generated. Center: {center_freq/1e6:.4f} MHz | Systems: {len(systems)}")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")

if __name__ == "__main__":
    update_config()

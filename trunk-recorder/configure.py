import os
import json
import sys

def update_config():
    template_path = '/app/default-config.json'
    output_path = '/data/config.json'
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found at {template_path}")
        return

    with open(template_path, 'r') as f:
        template_json = json.load(f)

    # --- 1. CONFIGURATION DETECTOR ---
    # Supports both new CHx_FREQ and legacy TR_CHANNELS_HZ variables
    ch1_raw = os.getenv('CH1_FREQ', os.getenv('TR_CHANNELS_HZ'))
    ch2_raw = os.getenv('CH2_FREQ')
    sdr_rate = int(os.getenv('SDR_RATE', '2400000'))
    
    # Identify which channels are active
    active_channels = []
    if ch1_raw: active_channels.append(int(ch1_raw))
    if ch2_raw: active_channels.append(int(ch2_raw))

    if not active_channels:
        print("❌ ERROR: No frequencies configured. Set CH1_FREQ or CH2_FREQ.")
        sys.exit(1)

    # --- 2. DYNAMIC SYSTEM & STREAM BUILDING ---
    systems = []
    streams = []
    
    # Process Channel 1
    if ch1_raw:
        systems.append({
            "label": os.getenv('CH1_LABEL', 'Channel 1'),
            "type": 'conventional' if os.getenv('CH1_TYPE', '').lower() == 'analog' else os.getenv('CH1_TYPE', 'conventional'),
            "shortName": "ch1",
            "channels": [int(ch1_raw)],
            "modulation": os.getenv('CH1_MOD', 'fm'),
            "squelch": int(os.getenv('CH1_SQUELCH', '-50')),
            "analogLevels": int(os.getenv('CH1_LEVELS', '15'))
        })
        streams.append({"shortName": "ch1", "TGID": 0, "address": "127.0.0.1", "port": int(os.getenv('CH1_UDP_PORT', 9123)), "sendJSON": False})

    # Process Channel 2
    if ch2_raw:
        systems.append({
            "label": os.getenv('CH2_LABEL', 'Channel 2'),
            "type": 'conventional' if os.getenv('CH2_TYPE', '').lower() == 'analog' else os.getenv('CH2_TYPE', 'conventional'),
            "shortName": "ch2",
            "channels": [int(ch2_raw)],
            "modulation": os.getenv('CH2_MOD', 'fm'),
            "squelch": int(os.getenv('CH2_SQUELCH', '-50')),
            "analogLevels": int(os.getenv('CH2_LEVELS', '15'))
        })
        streams.append({"shortName": "ch2", "TGID": 0, "address": "127.0.0.1", "port": int(os.getenv('CH2_UDP_PORT', 9124)), "sendJSON": False})

    # --- 3. BANDWIDTH & CENTER CALCULATION ---
    if len(active_channels) == 2:
        freq_diff = abs(active_channels[0] - active_channels[1])
        if freq_diff > (sdr_rate * 0.9):
            print(f"❌ ERROR: Frequencies too far apart ({freq_diff / 1000000:.2f} MHz).")
            sys.exit(1)
        center_hz = int(sum(active_channels) / 2)
    else:
        center_hz = active_channels[0]

    # --- 4. ASSEMBLE FINAL JSON ---
    config = template_json
    config["sources"][0]["center"] = center_hz
    config["sources"][0]["rate"] = sdr_rate
    config["sources"][0]["gain"] = int(os.getenv('TR_GAIN_DB', '40'))
    config["systems"] = systems
    config["plugins"][0]["streams"] = streams

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Generated {'Dual' if len(active_channels) == 2 else 'Single'} Channel Config")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_config()

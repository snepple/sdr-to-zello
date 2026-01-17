import os
import json

def update_config():
    template_path = '/app/default-config.json'
    output_path = '/data/config.json'
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found at {template_path}")
        return

    try:
        with open(template_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to parse template: {e}")
        return

    # 1. Audio/Filtering Settings from Balena
    call_timeout = int(os.getenv('TR_CALL_TIMEOUT', '1')) # Set to 1 to prevent "run-on"
    deemphasis = os.getenv('TR_DEEMPHASIS', 'true').lower() == 'true'
    min_duration = float(os.getenv('TR_MIN_DURATION', '0.5'))
    squelch = int(os.getenv('TR_SQUELCH_DB', '-55')) # Tighter squelch
    analog_levels = float(os.getenv('TR_ANALOG_LEVELS', '1.0'))
    
    # 2. SDR Settings (Lower rate = Lower CPU usage)
    gain = int(os.getenv('TR_GAIN_DB', '32'))
    rate = int(os.getenv('SDR_RATE', '1024000')) # Recommended lower rate
    center = int(os.getenv('TR_CENTER_HZ', '155115000'))

    # 3. Apply Settings to Config
    config["callTimeout"] = call_timeout
    config["ver"] = 2

    if "sources" in config and len(config["sources"]) > 0:
        source = config["sources"][0]
        source["center"] = center
        source["rate"] = rate
        source["gain"] = gain
        source["device"] = os.getenv('SDR_DEVICE', '0')

    if "systems" in config and len(config["systems"]) > 0:
        for system in config["systems"]:
            system["type"] = 'conventional'
            system["squelch"] = squelch
            system["analogLevels"] = analog_levels
            system["deemphasis"] = deemphasis
            system["minDuration"] = min_duration
            
            freq = os.getenv('TR_CHANNELS_HZ')
            if freq:
                system["channels"] = [int(freq)]

    # 4. Save Configuration
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Config generated. Timeout: {call_timeout}s | Rate: {rate}Hz | Squelch: {squelch}dB")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")

if __name__ == "__main__":
    update_config()

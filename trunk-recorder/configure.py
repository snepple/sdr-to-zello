import os
import json

def update_config():
    template_path = '/app/default-config.json'
    output_path = '/data/config.json'
    
    # 1. Load the template
    if not os.path.exists(template_path):
        print(f"❌ Template not found at {template_path}")
        return

    try:
        with open(template_path, 'r') as f:
            # Load as JSON object for programmatic manipulation
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to parse template: {e}")
        return

    # 2. Extract Environment Variables
    system_type = os.getenv('SYSTEM_TYPE', 'conventional')
    if system_type.lower() == 'analog':
        system_type = 'conventional'

    # Audio/Filtering Settings
    call_timeout = int(os.getenv('TR_CALL_TIMEOUT', '4'))
    deemphasis = os.getenv('TR_DEEMPHASIS', 'true').lower() == 'true'
    min_duration = float(os.getenv('TR_MIN_DURATION', '0.5'))
    squelch = int(os.getenv('TR_SQUELCH_DB', '-45'))
    analog_levels = float(os.getenv('TR_ANALOG_LEVELS', '1.0'))
    
    # SDR Settings
    gain = int(os.getenv('TR_GAIN_DB', '35'))
    rate = int(os.getenv('SDR_RATE', '2400000'))
    center = int(os.getenv('TR_CENTER_HZ', '155115000'))

    # 3. Apply Global Settings
    config["callTimeout"] = call_timeout
    config["ver"] = 2

    # 4. Update Source (SDR) Settings
    if "sources" in config and len(config["sources"]) > 0:
        source = config["sources"][0]
        source["center"] = center
        source["rate"] = rate
        source["gain"] = gain
        source["device"] = os.getenv('SDR_DEVICE', '0')

    # 5. Update System Settings
    if "systems" in config and len(config["systems"]) > 0:
        for system in config["systems"]:
            system["type"] = system_type
            system["squelch"] = squelch
            system["analogLevels"] = analog_levels
            system["deemphasis"] = deemphasis
            system["minDuration"] = min_duration
            
            # Update frequency/channels if provided
            freq = os.getenv('TR_CHANNELS_HZ')
            if freq:
                system["channels"] = [int(freq)]

    # 6. Write the final config to persistent storage
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Config generated at {output_path}")
        print(f"   Squelch: {squelch}dB | Gain: {gain}dB | Timeout: {call_timeout}s")
        print(f"   Deemphasis: {deemphasis} | MinDuration: {min_duration}s")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")

if __name__ == "__main__":
    update_config()

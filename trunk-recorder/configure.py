import os
import json

def update_config():
    # Use the default config as a base if it exists, or start with a skeleton
    template_path = '/app/default-config.json'
    output_path = '/data/config.json'
    
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            config = json.load(f)
    else:
        # Skeleton config if template is missing
        config = {
            "sources": [],
            "systems": [],
            "captureDir": "/data"
        }

    # 1. Setup Global/SDR Variables
    # Conventional is used for analog FM frequencies
    system_type = 'conventional' if os.getenv('SYSTEM_TYPE', 'conventional').lower() == 'analog' else os.getenv('SYSTEM_TYPE', 'conventional')
    
    freq1 = os.getenv('FREQ_1', '155115000')
    freq2 = os.getenv('FREQ_2', '155000000')
    
    # 2. Define System 1 (Primary)
    system1 = {
        "shortName": "sys_1",
        "type": system_type,
        "control_channels": [int(freq1)],
        "modulation": os.getenv('MODULATION', 'fm'),
        "squelch": int(os.getenv('TR_SQUELCH_DB', '-45')),
        "talkgroupsFile": "talkgroups1.csv",
        "audioStreaming": "true",
        "streamAddress": "127.0.0.1",
        "streamPort": 9123  # Routes to zellostream_1
    }

    # 3. Define System 2 (Secondary)
    system2 = {
        "shortName": "sys_2",
        "type": system_type,
        "control_channels": [int(freq2)],
        "modulation": os.getenv('MODULATION', 'fm'),
        "squelch": int(os.getenv('TR_SQUELCH_DB', '-45')),
        "talkgroupsFile": "talkgroups2.csv",
        "audioStreaming": "true",
        "streamAddress": "127.0.0.1",
        "streamPort": 9124  # Routes to zellostream_2
    }

    # 4. Apply Systems to Config
    config["systems"] = [system1, system2]
    
    # 5. Update SDR Source Settings
    # Center frequency should be set to cover both targets if they are close together
    if "sources" in config and len(config["sources"]) > 0:
        config["sources"][0]["center"] = int(os.getenv('TR_CENTER_HZ', freq1))
        config["sources"][0]["rate"] = int(os.getenv('SDR_RATE', '2400000'))
        config["sources"][0]["error"] = int(os.getenv('SDR_ERROR', '0'))
        config["sources"][0]["gain"] = int(os.getenv('TR_GAIN_DB', '45'))
        config["sources"][0]["serial"] = os.getenv('SDR_SERIAL', '00000001')

    # 6. Write the final config to the persistent /data directory
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"✅ Dual-Channel Config Generated at {output_path}")
        print(f"   System 1: {freq1}Hz -> Port 9123")
        print(f"   System 2: {freq2}Hz -> Port 9124")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")

if __name__ == "__main__":
    update_config()

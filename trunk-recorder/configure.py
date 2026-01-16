import os
import json

def update_config():
    template_path = '/app/default-config.json'
    output_path = '/data/config.json'
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found at {template_path}")
        return

    with open(template_path, 'r') as f:
        template_data = json.load(f)

    # 1. Setup Global Variables
    system_type = 'conventional' if os.getenv('SYSTEM_TYPE', 'conventional').lower() == 'analog' else os.getenv('SYSTEM_TYPE', 'conventional')
    
    # 2. Define System 1 (Primary)
    freq1 = os.getenv('FREQ_1', '155115000')
    system1 = {
        "shortName": "sys_1",
        "type": system_type,
        "control_channels": [int(freq1)],
        "modulation": os.getenv('MODULATION', 'fm'),
        "squelch": int(os.getenv('TR_SQUELCH_DB', '-45')),
        "audioStreaming": "true",
        "streamAddress": "127.0.0.1",
        "streamPort": 9123  # Port for Zello Stream 1
    }

    # 3. Define System 2 (Secondary)
    freq2 = os.getenv('FREQ_2', '155000000')
    system2 = {
        "shortName": "sys_2",
        "type": system_type,
        "control_channels": [int(freq2)],
        "modulation": os.getenv('MODULATION', 'fm'),
        "squelch": int(os.getenv('TR_SQUELCH_DB', '-45')),
        "audioStreaming": "true",
        "streamAddress": "127.0.0.1",
        "streamPort": 9124  # Port for Zello Stream 2
    }

    # 4. Apply to Template
    template_data["systems"] = [system1, system2]
    
    # Apply SDR settings
    if "sources" in template_data and len(template_data["sources"]) > 0:
        template_data["sources"][0]["center"] = int(os.getenv('TR_CENTER_HZ', freq1))
        template_data["sources"][0]["rate"] = int(os.getenv('SDR_RATE', '2400000'))
        template_data["sources"][0]["serial"] = os.getenv('SDR_SERIAL', '00000001')

    # 5. Write persistent config
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(template_data, f, indent=4)
        print(f"✅ Dual-Channel Config Generated at {output_path}")
        print(f"   System 1: {freq1} (Port 9123) | System 2: {freq2} (Port 9124)")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")

if __name__ == "__main__":
    update_config()

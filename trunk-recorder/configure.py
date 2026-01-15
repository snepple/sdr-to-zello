import os
import json

def update_config():
    template_path = '/app/default-config.json'
    output_path = '/data/config.json'
    
    # 1. Load the template
    if not os.path.exists(template_path):
        print(f"❌ Template not found at {template_path}")
        return

    with open(template_path, 'r') as f:
        config_str = f.read()

    # 2. Setup Variables with "conventional" as the safe default
    raw_system_type = os.getenv('SYSTEM_TYPE', 'conventional')
    
    # Correction logic: Trunk Recorder uses 'conventional' for analog FM
    if raw_system_type.lower() == 'analog':
        system_type = 'conventional'
    else:
        system_type = raw_system_type

    # 3. Replace placeholders with Dashboard Variables
    # Includes new CALL_TIMEOUT to stop audio clipping
    replacements = {
        "{TR_CENTER_HZ}": os.getenv('TR_CENTER_HZ', '155115000'),
        "{TR_CHANNELS_HZ}": os.getenv('TR_CHANNELS_HZ', '155115000'),
        "{SYSTEM_TYPE}": system_type,
        "{MODULATION}": os.getenv('MODULATION', 'fm'),
        "{SDR_SERIAL}": os.getenv('SDR_SERIAL', '00000001'),
        "{SQUELCH}": os.getenv('TR_SQUELCH_DB', '-45'),     # Improved sensitivity
        "{GAIN}": os.getenv('TR_GAIN_DB', '45'),           # Higher gain for faster trigger
        "{ANALOG_LEVELS}": os.getenv('TR_ANALOG_LEVELS', '15'),
        "{SDR_RATE}": os.getenv('SDR_RATE', '2400000'),
        "{CALL_TIMEOUT}": os.getenv('TR_CALL_TIMEOUT', '4') # Bridges gaps in speech
    }

    for placeholder, value in replacements.items():
        if value:
            config_str = config_str.replace(placeholder, str(value))

    # 4. Force write to the persistent /data directory
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(config_str)
        print(f"✅ Generated {output_path}")
        print(f"   Squelch: {replacements['{SQUELCH}']} | Gain: {replacements['{GAIN}']} | Timeout: {replacements['{CALL_TIMEOUT}']}s")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")

if __name__ == "__main__":
    update_config()

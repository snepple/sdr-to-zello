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

    # 2. Replace placeholders with Dashboard Variables
    # Format: {VARIABLE_NAME} -> value from Balena Dashboard
    replacements = {
        "{TR_CENTER_HZ}": os.getenv('TR_CENTER_HZ', '155115000'),
        "{TR_CHANNELS_HZ}": os.getenv('TR_CHANNELS_HZ', '155115000'),
        "{SYSTEM_TYPE}": os.getenv('SYSTEM_TYPE', 'analog'),
        "{MODULATION}": os.getenv('MODULATION', 'fm'),
        "{SDR_SERIAL}": os.getenv('SDR_SERIAL', '00000001')
    }

    for placeholder, value in replacements.items():
        if value:
            config_str = config_str.replace(placeholder, str(value))

    # 3. Force write to the persistent /data directory
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(config_str)
        print(f"✅ Successfully generated {output_path}")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")

if __name__ == "__main__":
    update_config()

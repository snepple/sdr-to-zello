import os
import json

def update_config():
    template_path = '/app/default-config.json'
    output_path = '/data/config.json'
    
    if not os.path.exists(template_path):
        print(f"❌ Template not found at {template_path}")
        return

    with open(template_path, 'r') as f:
        config_str = f.read()

    # Helper to clean system types
    def get_sys_type(env_name):
        val = os.getenv(env_name, 'conventional')
        return 'conventional' if val.lower() == 'analog' else val

    replacements = {
        # Global SDR Settings
        "{TR_CENTER_HZ}": os.getenv('TR_CENTER_HZ', '155115000'),
        "{GAIN}": os.getenv('TR_GAIN_DB', '40'),
        "{SDR_RATE}": os.getenv('SDR_RATE', '2400000'),

        # Channel 1 Variables
        "{CH1_LABEL}": os.getenv('CH1_LABEL', 'Channel 1'),
        "{CH1_FREQ}": os.getenv('CH1_FREQ', '155115000'),
        "{CH1_TYPE}": get_sys_type('CH1_TYPE'),
        "{CH1_MOD}": os.getenv('CH1_MOD', 'fm'),
        "{CH1_SQUELCH}": os.getenv('CH1_SQUELCH', '-50'),
        "{CH1_LEVELS}": os.getenv('CH1_LEVELS', '15'),

        # Channel 2 Variables
        "{CH2_LABEL}": os.getenv('CH2_LABEL', 'Channel 2'),
        "{CH2_FREQ}": os.getenv('CH2_FREQ', '158790000'),
        "{CH2_TYPE}": get_sys_type('CH2_TYPE'),
        "{CH2_MOD}": os.getenv('CH2_MOD', 'fm'),
        "{CH2_SQUELCH}": os.getenv('CH2_SQUELCH', '-50'),
        "{CH2_LEVELS}": os.getenv('CH2_LEVELS', '15')
    }

    for placeholder, value in replacements.items():
        config_str = config_str.replace(placeholder, str(value))

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(config_str)
        print(f"✅ Generated Dual Channel Config")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")

if __name__ == "__main__":
    update_config()

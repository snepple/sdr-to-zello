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
        config_str = f.read()

    # --- 1. FREQUENCY VALIDATION ---
    ch1_freq = int(os.getenv('CH1_FREQ', '155115000'))
    ch2_freq = int(os.getenv('CH2_FREQ', '158790000'))
    sdr_rate = int(os.getenv('SDR_RATE', '2400000'))
    
    # Calculate the spread
    freq_diff = abs(ch1_freq - ch2_freq)
    
    print(f"📡 Checking Bandwidth: Ch1: {ch1_freq}Hz | Ch2: {ch2_freq}Hz")
    print(f"📊 Frequency Spread: {freq_diff / 1000000:.2f} MHz")

    # Safety Check: The spread must be less than the sample rate (bandwidth)
    # We use 90% of the rate as a safety buffer for filter roll-off
    if freq_diff > (sdr_rate * 0.9):
        print(f"❌ ERROR: Frequencies are too far apart ({freq_diff / 1000000:.2f} MHz).")
        print(f"💡 Max spread allowed with {sdr_rate/1000000:.1f} MHz sample rate is {(sdr_rate * 0.9)/1000000:.2f} MHz.")
        sys.exit(1) # Halt the start to prevent silent failure
    else:
        print("✅ Bandwidth check passed.")

    # --- 2. CENTER FREQUENCY CALCULATION ---
    # Automatically set the SDR center to the middle of the two channels
    center_hz = int((ch1_freq + ch2_freq) / 2)

    # Helper to clean system types
    def get_sys_type(env_name):
        val = os.getenv(env_name, 'conventional')
        return 'conventional' if val.lower() == 'analog' else val

    replacements = {
        # Global SDR Settings (Auto-centered)
        "{TR_CENTER_HZ}": center_hz,
        "{GAIN}": os.getenv('TR_GAIN_DB', '40'),
        "{SDR_RATE}": sdr_rate,

        # Channel 1 Variables
        "{CH1_LABEL}": os.getenv('CH1_LABEL', 'Channel 1'),
        "{CH1_FREQ}": ch1_freq,
        "{CH1_TYPE}": get_sys_type('CH1_TYPE'),
        "{CH1_MOD}": os.getenv('CH1_MOD', 'fm'),
        "{CH1_SQUELCH}": os.getenv('CH1_SQUELCH', '-50'),
        "{CH1_LEVELS}": os.getenv('CH1_LEVELS', '15'),

        # Channel 2 Variables
        "{CH2_LABEL}": os.getenv('CH2_LABEL', 'Channel 2'),
        "{CH2_FREQ}": ch2_freq,
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
        print(f"✅ Generated Dual Channel Config (Centered at {center_hz} Hz)")
    except Exception as e:
        print(f"❌ Failed to write config: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_config()

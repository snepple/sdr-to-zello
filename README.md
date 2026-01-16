# SDR-to-Zello (Dual-Channel-v2)

This branch of the `sdr-to-zello` project is designed to monitor up to two independent radio frequencies simultaneously using a single RTL-SDR device. Each frequency is streamed to its own dedicated Zello channel.

## 🚀 Key Features
- **Dual-Channel Support**: Monitor two separate frequencies with independent Zello streams.
- **Unified Silence Sync**: Uses a single `SILENCE_SETTING` to keep the recorder and streamer perfectly timed, preventing audio clipping.
- **Automatic Centering**: Automatically calculates the optimal SDR center frequency based on your monitored frequencies.
- **Bandwidth Protection**: Validates that your frequencies are close enough together for the SDR hardware to hear both.

---

## 📋 Configuration (Environment Variables)

The system is configured via environment variables in the BalenaCloud dashboard. The `monitor.py` script automatically applies these settings across the services.

### 1. Required Variables
These must be set for the system to function.

| Variable | Description |
| :--- | :--- |
| `ZELLO_USERNAME` | Your Zello account username. |
| `ZELLO_PASSWORD` | Your Zello account password. |
| `FREQ_1` | Primary frequency in Hz (e.g., `158790000`). |
| `ZELLO_CHANNEL_1` | The name of the Zello channel for `FREQ_1`. |

### 2. Second Channel Variables
Set these to enable the secondary stream.

| Variable | Description |
| :--- | :--- |
| `FREQ_2` | Secondary frequency in Hz (e.g., `155000000`). |
| `ZELLO_CHANNEL_2` | The name of the Zello channel for `FREQ_2`. |

### 3. Tuning & Performance
These variables have built-in defaults but can be overridden for better performance.

| Variable | Default | Description |
| :--- | :--- | :--- |
| `SILENCE_SETTING` | `5` | Seconds to wait after speech ends before closing the stream (Prevents clipping). |
| `AUDIO_THRESHOLD` | `150` | Volume sensitivity for Zello. Higher values ignore more background noise. |
| `TR_SQUELCH_DB` | `-45` | Signal strength required to trigger the recorder (e.g., set to `-50` for weaker signals). |
| `SDR_RATE` | `2400000` | Bandwidth of the SDR in Hz (2.4 MHz). |
| `TR_SIGNAL_THRESHOLD` | `-55` | The minimum signal level to maintain an active recording. |
| `ZELLO_WORK_ACCOUNT` | *None* | Set this if using a Zello Work / Enterprise network. |

---

## 🛠️ How It Works

### Intelligent Centering
The `configure.py` script automatically calculates the midpoint between `FREQ_1` and `FREQ_2` to ensure both channels are within the SDR's capture window. If only one frequency is provided, it centers directly on that frequency.

### Bandwidth Safety
If the distance (spread) between your two frequencies is too wide for your `SDR_RATE`, the system will throw an error and stop. For a standard 2.4 MHz rate, your frequencies should ideally be within ~2.0 MHz of each other.

### Synchronized Timing
The `monitor.py` script ensures that the `SILENCE_SETTING` is converted correctly for both services:
* **Trunk-Recorder**: Receives the value in seconds.
* **ZelloStream**: Receives the value in milliseconds.

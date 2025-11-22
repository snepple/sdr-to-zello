

## Balena Service Variables
Configure these environment variables in your Balena dashboard at the Fleet or Device level.

### Required Zello Variables

```
ZELLO_USERNAME=
ZELLO_PASSWORD=
ZELLO_CHANNEL=
ZELLO_WORK_ACCOUNT=
```

### Optional Variables (defaults provided)

```
UDP_PORT=9123
INPUT_RATE=16000
ZELLO_RATE=16000
AUDIO_THRESHOLD=700
VOX_SILENCE_MS=2000
# Zello VOX can also be set directly in seconds (takes precedence over VOX_SILENCE_MS)
VOX_SILENCE_SECONDS=

# System Tuning Overrides (Unchanged)
TR_CHANNELS_HZ=154130000
TR_SQUELCH_DB=-50
TR_PLUGIN_PORT=9123
TR_PLUGIN_ADDRESS=127.0.0.1
TR_PLUGIN_TGID=0
TR_PLUGIN_SEND_JSON=false
```

### Multi-SDR Tuning Overrides (Index 1 to 5)

These variables configure the individual SDR devices. You must set at least `SDR_X_CENTER_HZ` for each SDR you want to use. The first source (`SDR_1_...`) corresponds to the first SDR device found by the system.

| Variable | Description | Example Value |
| :--- | :--- | :--- |
| **SDR\_X\_CENTER\_HZ** | Center frequency for SDR device 'X' (Required) | `154120625` |
| **SDR\_X\_SAMPLE\_RATE** | Sample rate for SDR device 'X' | `2048000` |
| **SDR\_X\_ERROR\_HZ** | PPM correction (frequency error) for SDR 'X' | `9375` |
| **SDR\_X\_GAIN\_DB** | Receiver gain for SDR device 'X' | `40` |
| **SDR\_X\_SIGNAL\_DETECTOR\_THRESHOLD** | Signal threshold for SDR device 'X' | `250` |

-----

### 💡 Example Configuration

To configure two SDRs, you would set:

| Variable | Value |
| :--- | :--- |
| `SDR_1_CENTER_HZ` | `154120625` |
| `SDR_1_SAMPLE_RATE` | `2048000` |
| `SDR_2_CENTER_HZ` | `854000000` |
| `SDR_2_SAMPLE_RATE` | `2400000` |

-----

## 3\. ✅ Verification Steps (Updated)

The log monitoring step should be updated to show how multiple SDRs would be initialized.

#### Step 2.2: Monitor Trunk Recorder Logs

Look for these success indicators for each configured SDR:

```
[INFO] Using device #0: RTL2832U
[INFO] Tuning to 154.120625 MHz (SDR 1)
[INFO] Using device #1: RTL2832U
[INFO] Tuning to 854.000000 MHz (SDR 2)
[INFO] SimpleStream plugin started on 127.0.0.1:9123
```

The video below gives an example of how Trunk Recorder is configured for decoding and recording P25 networks, which is useful context for the multi-SDR setup. [WarDragon SDRTrunk Test, Trunk-Recorder Setup, and CyberEther Quick Fix (Airspy R2, P25 Phase II) - YouTube](https://www.youtube.com/watch?v=VnsUIQAg-LI)

http://googleusercontent.com/youtube_content/3

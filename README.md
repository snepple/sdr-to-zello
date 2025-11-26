
# Configuration & Environment Variables

This project is configured entirely via **Environment Variables** in the Balena Dashboard. The startup scripts automatically generate the necessary JSON configuration files for `zellostream` and `trunk-recorder` based on these values.

## 1\. 🔐 Zello Credentials (Required)

These are required regardless of whether you are using an SDR or a Sound Card.

| Variable | Description |
| :--- | :--- |
| `ZELLO_USERNAME` | Your Zello username. |
| `ZELLO_PASSWORD` | Your Zello password. |
| `ZELLO_CHANNEL` | The name of the Zello channel to stream to. |
| `ZELLO_WORK_ACCOUNT` | (Optional) Leave empty for consumer Zello. Set this if using Zello Work. |

-----

## 2\. 🎛️ Input Mode Selection

You can configure this device to act as a **Trunk Recorder** (using USB SDR dongles) OR as a simple **RoIP Gateway** (using a physical scanner connected to a USB Sound Card).

### Option A: SDR Mode (Default)

Use this mode if you have RTL-SDR dongles plugged in.

  * **`TR_ENABLE_STREAMING`**: Set to `true` (default).
  * **`ZELLO_AUDIO_DEVICE`**: Do **not** set this variable (delete it if present).

### Option B: Sound Card / Scanner Mode

Use this mode if you are connecting a physical radio/scanner to a USB sound card or IMic.

  * **`TR_ENABLE_STREAMING`**: Set to `false`. (This disables the Trunk Recorder CPU usage).
  * **`ZELLO_AUDIO_DEVICE`**: Set to your ALSA device ID.
      * *Examples:* `default`, `hw:1,0`, `plughw:1,0`.
      * *Tip:* You can find this by opening the Terminal in Balena and running `arecord -l`.

-----

## 3\. 📻 Trunk Recorder Configuration (SDR Mode Only)

These variables control the `trunk-recorder` backend. They are translated from the [Official Trunk Recorder Config Docs](https://trunkrecorder.com/docs/CONFIGURE).

### System-Wide Settings

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TR_SYSTEM_TYPE` | `conventional` | `conventional`, `p25`, or `smartnet`. Use `conventional` for standard analog. |
| `TR_SYSTEM_MODULATION` | *Empty* | **Important for Analog:** Set to `fsk4` for P25, or leave empty/remove for Analog FM. |
| `TR_SQUELCH_DB` | `-50` | Signal strength required to record. **-60** is sensitive, **-40** is less sensitive. |
| `TR_CHANNEL_FILE` | *None* | Filename of a CSV in `/app/configs/` (e.g., `deltachannels.csv`). **Recommended for multi-channel setups.** |
| `TR_CHANNELS_HZ` | *None* | Comma-separated list of frequencies (e.g., `155115000,157485000`). Used only if no Channel File is provided. |

### Multi-SDR Tuning (Index 1 to 5)

Configure up to 5 SDRs. You must set at least `SDR_X_CENTER_HZ` to enable a device.

| Variable | Description | Recommended Value |
| :--- | :--- | :--- |
| **`SDR_X_CENTER_HZ`** | Center frequency for Device X. | *Target Freq* |
| **`SDR_X_SAMPLE_RATE`** | Bandwidth/Rate. | `2400000` (2.4 MS/s) or `2048000` |
| **`SDR_X_GAIN_DB`** | Receiver Gain. | `30` - `40` (Avoid Max/49.6 on VHF to prevent static) |
| **`SDR_X_ERROR_HZ`** | PPM Error correction. | `0` (unless stick is uncalibrated) |
| **`SDR_X_SIGNAL_DETECTOR_THRESHOLD`** | Digital signal detection sensitivity. | `10` (P25 only). Ignored if CSV sets Signal Detect to `false`. |

*\> Replace `X` with `1`, `2`, `3`, etc. (e.g., `SDR_1_CENTER_HZ`).*

-----

## 4\. 🔊 Audio & VOX Settings (Zellostream)

These variables control how audio is processed and sent to Zello. They are translated from the [Zellostream Documentation](https://github.com/aaknitt/zellostream).

| Variable | Default | Description |
| :--- | :--- | :--- |
| `VOX_SILENCE_MS` | `2000` | **Hang Time:** How many milliseconds of silence to wait before ending the transmission. Increase this if Zello cuts off mid-sentence. |
| `AUDIO_THRESHOLD` | `700` | **VOX Sensitivity:** Audio level (amplitude) required to trigger transmission. Lower = more sensitive. |
| `INPUT_RATE` | `16000` | Sample rate of the incoming audio. **Keep at 16000** for Trunk Recorder. |
| `UDP_PORT` | `9123` | Port used to receive audio from Trunk Recorder (SDR Mode Only). |

-----

## 5\. 📄 Channel Configuration (CSV Method)

For Analog systems or complex P25 setups, it is highly recommended to use a **Channel CSV** file instead of the simple `TR_CHANNELS_HZ` variable.

1.  Create a file (e.g., `mychannels.csv`) and add it to the `/app/configs/` folder in your repository.
2.  Set `TR_CHANNEL_FILE` = `mychannels.csv` in Balena.

**Format for Analog FM:**

```csv
TG Number,Frequency,Tone,Alpha Tag,Description,Tag,Category,Enable,Signal Detector,Squelch
1,155115000,0,Dispatch 1,Main Dispatch,Dispatch,EMS,true,false,-60
2,157485000,0,Ops 2,Operations,Ops,EMS,true,false,-60
```

*\> **Note:** For Analog, ensure `Signal Detector` is `false` and `Squelch` is set appropriately (e.g., -60).*

-----

## 6\. ✅ Verification & Troubleshooting

### Monitoring Logs

To verify the system is working, look for these indicators in the Balena logs:

**1. Zello Connection:**

```
zellostream I create_zello_connection: seq: 1
zellostream D main: recv: {"command":"on_channel_status","status":"online"...}
```

**2. SDR Initialization (Trunk Recorder):**

```
[info] Source Device: rtl=0
[info] Tuning to 155.115000 MHz
[info] [sys_1] Freq: 155.115000 MHz Squelch: -60 dB
```

**3. Active Recording (Analog):**
If you see `State: Idle`, the system is listening but hears silence.
When a transmission starts, you should see:

```
[sys_1] 0C TG: 1 Freq: 155.115000 MHz Starting Analog Recorder Num [8]
zellostream D udp_rx: got 314 bytes from ...
```

### Common Issues

  * **Zello restarting constantly:**
      * *Cause:* No audio is being received from the SDR.
      * *Fix:* Check if Trunk Recorder is running and if `UDP_PORT` matches.
  * **Constant Static / "Flood" of logs:**
      * *Cause:* Squelch is too low (e.g., -100) or Gain is too high (e.g., 49.6).
      * *Fix:* Set `TR_SQUELCH_DB` (or the CSV value) to `-60` or higher. Lower `SDR_X_GAIN_DB` to `35`.
  * **Recorder Stuck in "Idle":**
      * *Cause:* Signal Detector is enabled on a noisy Analog channel.
      * *Fix:* In your CSV, set `Signal Detector` to `false`.

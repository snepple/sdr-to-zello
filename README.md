# SDR to Zello Bridge (Dual Channel v2)

[cite_start]This project provides a two-service Docker stack that captures SDR audio via Trunk Recorder and streams it to two independent Zello channels using separate credentials and frequencies for each. [cite: 17, 19]

## Architecture

- [cite_start]**trunk-recorder**: Captures SDR audio from two different frequencies and publishes independent raw PCM streams via UDP. [cite: 19]
- [cite_start]**zellostream**: Ingests multiple UDP audio streams and routes them to specific Zello accounts using voice activation (VOX). [cite: 17, 19]

## Configuration

Set these environment variables in the Balena dashboard. [cite_start]The services automatically inject these into the system configuration at startup. [cite: 17, 7]

### Zello Streaming Variables

| Variable | Requirement | Default | Description |
| :--- | :--- | :--- | :--- |
| `ZELLO_USERNAME` | **Mandatory** | None | [cite_start]Username for the primary Zello account. [cite: 17] |
| `ZELLO_PASSWORD` | **Mandatory** | None | [cite_start]Password for the primary Zello account. [cite: 17] |
| `ZELLO_CHANNEL` | **Mandatory** | None | [cite_start]Primary Zello channel name. [cite: 17] |
| `ZELLO_USERNAME_2` | Optional | None | [cite_start]Username for the secondary Zello account. [cite: 17] |
| `ZELLO_PASSWORD_2` | Optional | None | [cite_start]Password for the secondary Zello account. [cite: 17] |
| `ZELLO_CHANNEL_2` | Optional | None | [cite_start]Secondary Zello channel name. [cite: 17] |
| `ZELLO_WORK_ACCOUNT`| Optional | None | [cite_start]Zello Work network name (leave empty for consumer accounts). [cite: 17] |
| `AUDIO_THRESHOLD` | Optional | `700` | [cite_start]VOX energy level to trigger transmission (Increase to reduce sensitivity). [cite: 17] |
| `MIN_DURATION_MS` | Optional | `0` | [cite_start]Ignores transmissions shorter than this value (filters static "clicks"). [cite: 17] |

### Trunk Recorder & Hardware Variables

| Variable | Requirement | Default | Description |
| :--- | :--- | :--- | :--- |
| `CENTER_FREQ` | **Mandatory** | None | The center frequency (MHz) for the SDR hardware (e.g., `155.115`). |
| `TALKGROUP_FREQ` | **Mandatory** | None | The primary frequency (MHz) to monitor for the first Zello channel. |
| `TALKGROUP_FREQ_2` | Optional | None | The secondary frequency (MHz) to monitor for the second Zello channel. |
| `SDR_GAIN` | Optional | `40` | RF gain for the RTL-SDR dongle (typical max is 49.6). |
| `SDR_PPM` | Optional | `0` | Frequency correction (PPM) for hardware drift. |
| `SQUELCH` | Optional | `-40` | Signal level threshold for analog audio (Lower = more sensitive). |
| `SYSTEM_TYPE` | Optional | `analog` | Defines the radio system type (`analog` or `p25`). |
| `TALKGROUP_ID` | Optional | `1` | The specific talkgroup ID to monitor for the primary frequency. |
| `TALKGROUP_ID_2` | Optional | `2` | The specific talkgroup ID to monitor for the secondary frequency. |

## Troubleshooting

### VOX Tuning
- [cite_start]**Constant Transmitting**: Increase `AUDIO_THRESHOLD` (try 1000-1500) or set `MIN_DURATION_MS` to 300 to filter static bursts. [cite: 17, 19]
- [cite_start]**Chopped Audio**: Decrease `AUDIO_THRESHOLD` (try 400-500) so quieter voices trigger the stream. [cite: 19]

### Hardware & Logs
- **No Signal**: Check `SDR_PPM` correction or ensure `CENTER_FREQ` is within 1MHz of both monitored frequencies.
- [cite_start]**Verify Connection**: Check Balena logs to confirm both Zello accounts have authenticated successfully. [cite: 19]

## License
[cite_start]Refer to the respective licenses for [Trunk Recorder](https://github.com/TrunkRecorder/trunk-recorder) and [ZelloStream](https://github.com/aaknitt/zellostream). [cite: 19]

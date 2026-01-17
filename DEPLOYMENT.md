# SDR to Zello Bridge (Dual Channel v2)

This project provides a two-service Docker stack that captures SDR audio via Trunk Recorder and streams it to two independent Zello channels using separate credentials and frequencies for each.

## Architecture

- **trunk-recorder**: Captures SDR audio from two different frequencies and publishes independent raw PCM streams via UDP ports 9123 and 9124.
- **zellostream**: Ingests multiple UDP audio streams and routes them to specific Zello accounts using voice activation (VOX).

## Configuration

Set these environment variables in the Balena dashboard. The services automatically inject these into the system configuration at startup.

### Zello Streaming Variables

| Variable | Requirement | Default | Description |
| :--- | :--- | :--- | :--- |
| `ZELLO_USERNAME_1` | **Mandatory** | None | Username for the primary Zello account. |
| `ZELLO_PASSWORD_1` | **Mandatory** | None | Password for the primary Zello account. |
| `ZELLO_CHANNEL_1` | **Mandatory** | None | Primary Zello channel name. |
| `ZELLO_USERNAME_2` | Optional | None | Username for the secondary Zello account. |
| `ZELLO_PASSWORD_2` | Optional | None | Password for the secondary Zello account. |
| `ZELLO_CHANNEL_2` | Optional | None | Secondary Zello channel name. |
| `ZELLO_WORK_ACCOUNT`| Optional | None | Zello Work network name (leave empty for consumer accounts). |
| `AUDIO_THRESHOLD` | Optional | `700` | VOX energy level to trigger transmission (Increase to reduce sensitivity). |
| `MIN_DURATION_MS` | Optional | `0` | Ignores transmissions shorter than this value (filters static "clicks"). |

### Trunk Recorder & Hardware Variables

| Variable | Requirement | Default | Description |
| :--- | :--- | :--- | :--- |
| `FREQ_1` | **Mandatory** | None | The primary frequency (Hz) to monitor (e.g., `155115000`). |
| `FREQ_2` | Optional | None | The secondary frequency (Hz) to monitor (e.g., `155225000`). |
| `SQUELCH_1` | Optional | `TR_SQUELCH_DB` | Specific squelch for FREQ_1. |
| `SQUELCH_2` | Optional | `TR_SQUELCH_DB` | Specific squelch for FREQ_2. |
| `TR_SQUELCH_DB` | Optional | `-45` | Global squelch threshold used if specific SQUELCH_X is not set. |
| `SDR_RATE` | Optional | `2400000` | Sample rate for the SDR hardware. |
| `TR_GAIN_DB` | Optional | `45` | RF gain for the RTL-SDR dongle. |
| `SYSTEM_TYPE` | Optional | `conventional` | Radio system type (`analog` translates to `conventional`). |
| `TR_CENTER_HZ` | Optional | Auto | Manual override for the SDR center frequency. |
| `SDR_SERIAL` | Optional | `00000001`| Serial number of the specific SDR device to use. |

# SDR to Zello Bridge (Dual Channel v2)

This project provides a two-service Docker stack that captures SDR audio via Trunk Recorder and streams it to multiple Zello channels using separate credentials for each.

## Architecture

- **trunk-recorder**: Captures SDR audio and publishes raw PCM via UDP port 9123 using the SimpleStream plugin.
- **zellostream**: Ingests UDP audio and streams it to Zello channels with voice activation (VOX) and independent account support.

## Configuration

### Balena Service Variables

Set these environment variables in the Balena dashboard. The `zellostream` service injects these into the configuration at startup.

#### Primary Channel (Required)
- `ZELLO_USERNAME`: Username for the first Zello account.
- `ZELLO_PASSWORD`: Password for the first Zello account.
- `ZELLO_CHANNEL`: Target name for the first channel.

#### Secondary Channel (Optional)
- `ZELLO_USERNAME_2`: Username for the second Zello account.
- `ZELLO_PASSWORD_2`: Password for the second Zello account.
- `ZELLO_CHANNEL_2`: Target name for the second channel.

#### Global Settings (Optional Defaults)
- `ZELLO_WORK_ACCOUNT`: Zello Work network name (leave empty for consumer Zello).
- `UDP_PORT=9123`: UDP port for audio pipeline.
- `INPUT_RATE=16000`: Audio input sample rate.
- `ZELLO_RATE=16000`: Zello output sample rate.
- `AUDIO_THRESHOLD=700`: VOX activation energy threshold (increase to reduce sensitivity).
- `MIN_DURATION_MS=0`: Filters out transmissions shorter than this value (useful for ignoring static "clicks").

## Troubleshooting

### VOX Tuning
- **No activation**: Lower `AUDIO_THRESHOLD` (e.g., try 300-500).
- **False triggering**: Raise `AUDIO_THRESHOLD` (e.g., try 1000+) or set `MIN_DURATION_MS` to 300 to ignore short bursts of static.

### Verification
You can monitor the authentication status and connection of both accounts in the `zellostream` container logs. Each account will report its connection status independently.
```bash
# Check ZelloStream logs
balena logs <device-uuid> --service zellostream

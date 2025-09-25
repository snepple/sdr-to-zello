# SDR to Zello Bridge

This project provides a two-service Docker stack that captures SDR audio via Trunk Recorder and streams it to Zello channels using ZelloStream.

## Architecture

- **trunk-recorder**: Captures SDR audio and publishes raw PCM via UDP port 9123 using the SimpleStream plugin
- **zellostream**: Ingests UDP audio and streams it to a Zello channel with voice activation (VOX)

## Quick Start

### Prerequisites

- Balena Cloud account and device
- RTL-SDR dongle
- Zello account with channel access
- GitHub repository with Actions enabled

### Deployment

#### Option 1: Automated GitHub Deployment (Recommended)
1. Fork this repository
2. Configure GitHub secrets (see [DEPLOYMENT.md](DEPLOYMENT.md))
3. Configure Balena Service Variables in your dashboard
4. Push to `main` branch - deployment happens automatically!

#### Option 2: Manual Balena Push
1. Clone this repository
2. Install Balena CLI: `npm install -g balena-cli`
3. Login: `balena login`
4. Push: `balena push sam27/md3zello`

📖 **See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup instructions**

## Configuration

### Balena Service Variables

Set these environment variables in Balena dashboard (Device or Fleet level):

**Required:**
- `ZELLO_USERNAME`: Your Zello username
- `ZELLO_PASSWORD`: Your Zello password
- `ZELLO_CHANNEL`: Target channel name (e.g., "Clinton")
- `ZELLO_WORK_ACCOUNT`: Zello Work account name (or empty for consumer Zello)

**Optional (have defaults):**
- `UDP_PORT=9123`: UDP port for audio pipeline
- `INPUT_RATE=8000`: Audio input sample rate
- `ZELLO_RATE=16000`: Zello output sample rate
- `AUDIO_THRESHOLD=700`: VOX activation threshold
- `VOX_SILENCE_MS=2000`: Silence time before stopping transmission

### Config Files

The `configs/` directory contains:

- `configs/trunk-recorder.json`: Trunk Recorder configuration (ready to use)
- `configs/zello.json`: ZelloStream template (credentials injected via env vars)

No manual config file editing needed - everything is handled via Balena Service Variables!

## Troubleshooting

### SDR Access Issues
- Ensure `privileged: true` is set in docker-compose.yml
- Check that `/dev/bus/usb` is properly mounted
- DVB drivers are automatically unloaded by the entrypoint script

### VOX Tuning
- **No activation**: Lower `AUDIO_THRESHOLD` (try 500)
- **False triggering**: Raise `AUDIO_THRESHOLD` (try 1000-1400) or increase `VOX_SILENCE_MS`

### Audio Pipeline
- Verify UDP traffic: `tcpdump -n -i any udp port 9123`
- Check container logs for connection and authentication status

## Verification Checklist

- [ ] `lsusb` shows RTL2832U device in trunk-recorder container
- [ ] Trunk Recorder logs show tuning and SimpleStream plugin active
- [ ] `ss -u -l | grep 9123` shows bound UDP port in zellostream container
- [ ] UDP traffic visible during radio activity
- [ ] ZelloStream logs show successful Zello authentication
- [ ] Audio appears in target Zello channel
- [ ] VOX operates without false triggers or missed activations

## Development

### Building Images Locally

```bash
# Build trunk-recorder
docker build -t trunk-recorder ./trunk-recorder

# Build zellostream
docker build -t zellostream ./zellostream
```

### Testing

```bash
# Start services
docker-compose up

# Check UDP listener
docker-compose exec zellostream ss -u -l | grep 9123

# Monitor UDP traffic
sudo tcpdump -n -i any udp port 9123
```

## License

This project integrates:
- [Trunk Recorder](https://github.com/TrunkRecorder/trunk-recorder)
- [ZelloStream](https://github.com/aaknitt/zellostream)

Refer to their respective licenses for usage terms.
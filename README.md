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

## Verification Steps

### 1. Check Device Health in Balena Dashboard
- Both services should show "Running" status
- Health checks should pass (green checkmarks)
- No restart loops or error states

### 2. Verify Hardware Detection
```bash
# In trunk-recorder container terminal (via Balena dashboard)
lsusb | grep RTL2832U
# Should show: Bus 001 Device 002: ID 0bda:2838 Realtek RTL2832U DVB-T

# Check for kernel driver conflicts
dmesg | grep dvb
# Should be clean or show drivers unloaded
```

### 3. Monitor Trunk Recorder Logs
Look for these key indicators:
```
[INFO] Using device #0: RTL2832U
[INFO] Tuning to 154.12 MHz
[INFO] SimpleStream plugin started on 127.0.0.1:9123
```

### 4. Verify UDP Audio Stream
```bash
# In zellostream container terminal
ss -u -l | grep 9123
# Should show: UNCONN  0  0  127.0.0.1:9123

# Monitor UDP traffic (if tcpdump available)
tcpdump -n -i any udp port 9123
# Should show packets when radio activity occurs
```

### 5. Check ZelloStream Authentication
Monitor zellostream logs for:
```
[INFO] Successfully authenticated with Zello
[INFO] Connected to channel: Clinton
[DEBUG] Audio threshold: 700, VOX silence: 2000ms
```

### 6. Test End-to-End Audio Flow
1. **Radio Activity**: Wait for or trigger radio traffic on 154.13 MHz
2. **Trunk Recorder**: Should log "Recording started" messages
3. **UDP Stream**: Should see packets in tcpdump or netstat activity
4. **ZelloStream**: Should log "Audio above threshold, transmitting"
5. **Zello Channel**: Audio should appear in "Clinton" channel

### Troubleshooting Checklist

- [ ] RTL-SDR hardware detected by trunk-recorder
- [ ] No "device busy" errors (DVB drivers properly unloaded)
- [ ] Trunk Recorder tuned to correct frequency (154.120625 MHz center, 154.13 MHz channel)
- [ ] SimpleStream plugin active on UDP port 9123
- [ ] ZelloStream bound to UDP port 9123
- [ ] ZelloStream successfully authenticated to Zello
- [ ] Connected to correct Zello channel
- [ ] VOX threshold appropriate (no false triggers or missed audio)
- [ ] Audio quality good in Zello channel

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
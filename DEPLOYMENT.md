# Deployment Guide

## GitHub Secrets Setup

To enable automated deployment to Balena, configure the following secrets in your GitHub repository:

### Required Secrets

1. **Navigate to GitHub Repository Settings**
   - Go to your repository on GitHub
   - Click on "Settings" tab
   - Select "Secrets and variables" → "Actions"

2. **Add Required Secrets**
   - Click "New repository secret"
   - Add the following secrets:

   ```
   Name: BALENA_API_TOKEN
   Value: 
   ```

### Balena Fleet Configuration

- **Fleet Name**: `sam27/md3zello`
- **Target Device**: Raspberry Pi (configured in Balena dashboard)

## Balena Service Variables

Configure these environment variables in your Balena dashboard at the Fleet or Device level:

### Required Variables

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
```

### SDR Gain

- The default config sets the RTL-SDR gain to `40` dB (`configs/trunk-recorder.json`).
- Adjust this value to match your hardware/noise floor; use tools like GQRX or `rtl_test -t` to determine the best setting.

## Deployment Methods

### Automatic Deployment
- Push to `main` branch triggers automatic deployment
- Creates live release (devices update automatically)

### Manual Deployment
1. Go to "Actions" tab in GitHub repository
2. Select "Deploy to Balena" workflow
3. Click "Run workflow"
4. Choose options:
   - **Branch**: main
   - **Create draft release**: Check to create draft (for testing)

### Direct Balena Push (Alternative)
```bash
# Install Balena CLI
npm install -g balena-cli

# Login to Balena
balena login

# Push to fleet
balena push sam27/md3zello
```

## Verification Steps

### 1. Check Balena Dashboard
- **Release Status**: Verify release is created and downloaded to device
- **Service Status**: Both `trunk-recorder` and `zellostream` should show "Running"
- **Health Checks**: Green checkmarks for both services
- **Device Status**: Online and accessible

### 2. Verify Audio Pipeline
Follow these steps in order to confirm end-to-end functionality:

#### Step 2.1: Check RTL-SDR Hardware
```bash
# Access trunk-recorder container terminal via Balena dashboard
lsusb | grep RTL2832U
# Expected: Bus 001 Device 002: ID 0bda:2838 Realtek RTL2832U DVB-T
```

#### Step 2.2: Monitor Trunk Recorder Logs
Look for these success indicators:
```
[INFO] Using device #0: RTL2832U
[INFO] Tuning to 154.120625 MHz
[INFO] SimpleStream plugin started on 127.0.0.1:9123
```

#### Step 2.3: Confirm SimpleStream Plugin
```bash
# Inside trunk-recorder container
ls /usr/local/lib/trunk-recorder/plugins | grep simplestream
# Expected: libsimplestream.so
```

#### Step 2.4: Verify UDP Stream
```bash
# In zellostream container terminal
ss -u -l | grep 9123
# Expected: UNCONN  0  0  127.0.0.1:9123
```

#### Step 2.5: Check ZelloStream Authentication
Monitor logs for:
```
[INFO] Successfully authenticated with Zello
[INFO] Connected to channel: Clinton
[DEBUG] Audio threshold: 700, VOX silence: 2000ms
```

#### Step 2.6: Test Live Audio Flow
1. Wait for radio activity on 154.13 MHz (Clinton Fire frequency)
2. Trunk Recorder should log activity and start streaming
3. ZelloStream should detect audio above threshold (700)
4. Audio should appear in Zello channel "Clinton"

### 3. Success Criteria
- ✅ RTL-SDR hardware detected and accessible
- ✅ Trunk Recorder tuned to correct frequency
- ✅ SimpleStream plugin active on UDP port 9123
- ✅ ZelloStream authenticated to Zello Work account "md3md3"
- ✅ Connected to Zello channel "Clinton"
- ✅ Audio streaming from radio to Zello channel
- ✅ VOX working properly (no false triggers, catches all audio)

## Troubleshooting

### Build Failures
- Check GitHub Actions logs
- Verify all secrets are set correctly
- Ensure Balena API token has fleet access

### Deployment Issues
- Check Balena dashboard for error messages
- Verify device is online and accessible
- Review service variables configuration

### Audio Issues
- Verify RTL-SDR hardware detection
- Check UDP port binding
- Review Zello authentication logs
- Test VOX threshold settings

## Security Notes

- API tokens and credentials are stored securely in GitHub secrets
- No sensitive data is committed to the repository
- Environment variables are injected at runtime via Balena
- Config files contain only placeholder values

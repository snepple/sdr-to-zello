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
INPUT_RATE=8000
ZELLO_RATE=16000
AUDIO_THRESHOLD=700
VOX_SILENCE_MS=2000
```

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

1. **Check Balena Dashboard**
   - Verify release is created
   - Monitor build progress
   - Check device download status

2. **Device Health Checks**
   - Both services should show "Running"
   - Health checks should pass
   - Logs should show successful initialization

3. **Audio Pipeline Test**
   - Trunk Recorder should detect RTL-SDR
   - UDP traffic on port 9123
   - ZelloStream should authenticate successfully
   - Audio should appear in Zello channel "Clinton"

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

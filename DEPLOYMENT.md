# Deployment Guide

## GitHub Secrets Setup

To enable automated deployment to Balena, configure the following secrets in your GitHub repository:

### Required Secret

1. **Navigate to GitHub Repository Settings**
   - Go to your repository on GitHub.
   - Click on the "Settings" tab.
   - Select "Secrets and variables" → "Actions".

2. **Add Required Secret**
   - Click "New repository secret".
   - **Name**: `BALENA_API_TOKEN`
   - **Value**: [Your Balena API Key]

---

## Balena Service Variables

Configure these environment variables in your Balena dashboard at the **Fleet** or **Device** level. The system now supports two independent channels monitored by a single SDR.

### Mandatory Variables (Must be set for the system to start)

#### **Global SDR Settings**
- **`TR_CENTER_HZ`**: The center frequency for the SDR (e.g., `156500000`).
- **`SDR_RATE`**: Sample rate, typically `2400000` for Nooelec v5.
- **`SDR_SERIAL`**: The serial number of your RTL-SDR (default: `00000001`).

#### **Channel 1 (Primary)**
- **`CH1_LABEL`**: The display name for Channel 1 (e.g., `Delta Ambulance`).
- **`CH1_FREQ`**: Frequency in Hz (e.g., `155115000`).
- **`CH1_USERNAME`**: Zello username for this stream.
- **`CH1_PASSWORD`**: Zello password.
- **`CH1_CHANNEL`**: Zello channel name.
- **`CH1_WORK_ACCOUNT`**: Your Zello Work network name.

#### **Channel 2 (Secondary)**
- **`CH2_LABEL`**: The display name for Channel 2 (e.g., `Sidney Fire`).
- **`CH2_FREQ`**: Frequency in Hz (e.g., `158790000`).
- **`CH2_USERNAME`**: Zello username for the second stream.
- **`CH2_PASSWORD`**: Zello password.
- **`CH2_CHANNEL`**: Zello channel name.
- **`CH2_WORK_ACCOUNT`**: Zello Work network name.

---

### Optional Tuning Variables (Defaults provided)

| Variable | Default | Description |
| :--- | :--- | :--- |
| **`CH1_SQUELCH`** | `-50` | Squelch level for Channel 1 (Higher = tighter). |
| **`CH2_SQUELCH`** | `-50` | Squelch level for Channel 2 (Adjust if hearing static). |
| **`CH1_UDP_PORT`** | `9123` | UDP port for Channel 1 audio. |
| **`CH2_UDP_PORT`** | `9124` | UDP port for Channel 2 audio. |
| **`TR_GAIN_DB`** | `40` | RTL-SDR hardware gain. |
| **`VOX_SILENCE_MS`** | `3000` | How long to wait before ending a transmission (ms). |
| **`BALENA_HOST_CONFIG_reboot_at`** | `None` | Cron expression for scheduled maintenance reboots. |

---

## Verification Steps

### 1. Bandwidth Check
The `configure.py` script automatically verifies that your two chosen frequencies are within **2.4 MHz** of each other. If they are too far apart, the service will fail to start and log an error.

### 2. Monitor Dual Streams
Access the Balena logs. You should see two distinct Zello processes starting:
```text
[CH1] Starting ZelloStream for user: DeltaAmbulance
[CH2] Starting ZelloStream for user: SidneyFire
[CH1] Connected to channel: Delta Ambulance
[CH2] Connected to channel: Sidney Fire Rescue

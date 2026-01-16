FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    dumb-init \
    ffmpeg \
    libasound2 \
    libpulse0 \
    libportaudio2 \
    libsndfile1 \
    pkg-config \
    portaudio19-dev \
    python3-dev \
    curl \
    dos2unix \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
# ADDED: websocket-client (Required for Zello login)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests croniter websocket-client

# COPY the files from your local computer
# Note: Ensure these paths match your local folder structure
COPY zellostream/run.py /app/run.py
COPY zellostream/zellostream.py /app/zellostream.py
COPY zellostream/start.sh /app/start.sh

# OPTIONAL: Copy config if you have one locally, otherwise the script uses env vars
# COPY configs/zello.json /app/config.json

RUN dos2unix /app/start.sh /app/run.py /app/zellostream.py && \
    chmod +x /app/start.sh

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/app/start.sh"]

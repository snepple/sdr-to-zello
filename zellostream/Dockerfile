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
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests croniter

# COPY THE FILES FROM YOUR COMPUTER (This is the fix)
COPY zellostream/run.py /app/run.py
COPY zellostream/zellostream.py /app/zellostream.py
COPY zellostream/start.sh /app/start.sh

RUN dos2unix /app/start.sh /app/run.py /app/zellostream.py && \
    chmod +x /app/start.sh

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/app/start.sh"]

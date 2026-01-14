FROM python:3.11-slim

# Install system dependencies + dos2unix + netcat for healthcheck bypass
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    dumb-init \
    ffmpeg \
    git \
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

# 1. Clone the repository base
RUN git clone --depth 1 https://github.com/aaknitt/zellostream.git /tmp/repo \
    && cp -r /tmp/repo/* /app/ \
    && rm -rf /tmp/repo

# 2. Install requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests && \
    if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    fi

# 3. Copy your custom scripts
COPY zellostream/run.py /app/run.py
COPY zellostream/start.sh /app/start.sh
COPY configs/zello.json /app/default-config.json

# 4. CRITICAL: Convert Windows line endings to Linux and set permissions
RUN dos2unix /app/start.sh /app/run.py && \
    chmod +x /app/start.sh /app/run.py

ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Execute using absolute path
CMD ["/bin/bash", "/app/start.sh"]

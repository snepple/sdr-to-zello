FROM python:3.11-slim

# Install system dependencies
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
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Clone the base code
RUN git clone --depth 1 https://github.com/aaknitt/zellostream.git /app

# 2. Install requirements + requests for Telegram
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests && \
    if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    fi

# 3. OVERLAY your custom logic (This ensures your files win over the git versions)
# Note: Use the relative path from the project root
COPY zellostream/run.py /app/run.py
COPY zellostream/start.sh /app/start.sh
COPY configs/zello.json /app/default-config.json

# 4. Permissions
RUN chmod +x /app/run.py /app/start.sh

# signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Run the startup script
CMD ["/app/start.sh"]

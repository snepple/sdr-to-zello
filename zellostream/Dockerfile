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

# Set Working Directory
WORKDIR /app

# 1. CLONE FIRST: Pull the base code from GitHub
RUN git clone --depth 1 https://github.com/aaknitt/zellostream.git .

# 2. INSTALL LIBS: Install requirements + Telegram 'requests'
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests && \
    if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    fi

# 3. OVERWRITE: Copy your custom local files into the container
# This ensures these files exist at /app/start.sh and /app/run.py
COPY zellostream/run.py /app/run.py
COPY zellostream/start.sh /app/start.sh
COPY configs/zello.json /app/default-config.json

# 4. PERMISSIONS: Explicitly make them executable
RUN chmod +x /app/start.sh /app/run.py

# Set signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Run the startup script
CMD ["/app/start.sh"]

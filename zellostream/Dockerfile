FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    dumb-init \
    ffmpeg \
    gfortran \
    git \
    libasound2 \
    libblas-dev \
    libopenblas-dev \
    libffi-dev \
    libpulse-dev \
    libpulse0 \
    libportaudio2 \
    libsndfile1 \
    llvm \
    libopenblas0 \
    pkg-config \
    portaudio19-dev \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone the repository
RUN git clone --depth 1 https://github.com/aaknitt/zellostream.git /app

# Set environment for LLVM (required for some audio processing libs)
ENV LLVM_CONFIG=/usr/bin/llvm-config

# Install Python requirements and add 'requests' for Telegram notifications
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests && \
    if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    fi

# Copy custom scripts and configurations
COPY zellostream/run.py /app/run.py
COPY configs/zello.json /app/default-config.json
COPY zellostream/start.sh /app/start.sh

# Ensure scripts are executable
RUN chmod +x /app/run.py /app/start.sh

# Keep dumb-init for signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Execute the staggered startup script
CMD ["/app/start.sh"]

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

# 1. Clone the repository into a SUBFOLDER first to avoid overwriting /app
RUN git clone --depth 1 https://github.com/aaknitt/zellostream.git /tmp/repo \
    && cp -r /tmp/repo/* /app/ \
    && rm -rf /tmp/repo

# 2. Install Python requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir requests && \
    if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt; \
    fi

# 3. FORCE COPY: We use the '*' to ensure we grab the files regardless of context
# We copy them to /app/ explicitly
COPY zellostream/run.py /app/run.py
COPY zellostream/start.sh /app/start.sh
COPY configs/zello.json /app/default-config.json

# 4. Final Sanity Check & Permissions
RUN ls -l /app/start.sh && chmod +x /app/start.sh /app/run.py

ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Use the absolute path
CMD ["/bin/bash", "/app/start.sh"]

FROM python:3.11-slim

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
RUN git clone --depth 1 https://github.com/aaknitt/zellostream.git /app

# If repo has a requirements.txt, install it (ignore if absent)
ENV LLVM_CONFIG=/usr/bin/llvm-config

RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir --upgrade pip; \
      pip install --no-cache-dir -r requirements.txt; \
    fi

COPY zellostream/run.py /app/run.py
COPY configs/zello.json /app/default-config.json
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3", "/app/run.py"]

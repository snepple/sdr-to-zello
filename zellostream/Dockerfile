FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg dumb-init git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN git clone --depth 1 https://github.com/aaknitt/zellostream.git /app

# If repo has a requirements.txt, install it (ignore if absent)
RUN [ -f requirements.txt ] && pip install --no-cache-dir -r requirements.txt || true

COPY run.py /app/run.py
COPY configs/zello.json /app/default-config.json
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["python3", "/app/run.py"]

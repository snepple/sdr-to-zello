FROM debian:bookworm

RUN apt-get update && apt-get install -y \
    git build-essential cmake pkg-config ca-certificates curl jq \
    libboost-all-dev librtlsdr-dev rtl-sdr \
    libsndfile1-dev libzmq3-dev libsox-dev sox \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN git clone --depth 1 https://github.com/TrunkRecorder/trunk-recorder.git
WORKDIR /opt/trunk-recorder
RUN mkdir build && cd build && cmake .. && make -j$(nproc) && make install

# runtime
WORKDIR /
RUN mkdir -p /data/configs /data/logs
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
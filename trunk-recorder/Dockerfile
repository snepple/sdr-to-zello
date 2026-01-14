# Stage 1 - Build Stage
FROM ubuntu:24.04 AS builder

# Install build dependencies
RUN apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install --no-install-recommends -y \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        git \
        pkg-config \
        wget \
        python3-six \
        gnuradio-dev \
        gr-osmosdr \
        libosmosdr-dev \
        libairspy-dev \
        libairspyhf-dev \
        libfreesrp-dev \
        libhackrf-dev \
        librtlsdr-dev \
        libuhd-dev \
        libusb-dev \
        libusb-1.0-0-dev \
        libsoapysdr-dev \
        libsox-dev \
        libboost-all-dev \
        libcurl4-openssl-dev \
        libgmp-dev \
        liborc-0.4-dev \
        libpthread-stubs0-dev \
        libsndfile1-dev \
        libssl-dev \
        libzmq3-dev \
        sox \
        ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Clone and build Trunk Recorder
WORKDIR /src
RUN git clone --depth 1 https://github.com/TrunkRecorder/trunk-recorder.git .

# Enable SimpleStream plugin
RUN sed -i 's/#add_subdirectory(plugins\/simplestream)/add_subdirectory(plugins\/simplestream)/' CMakeLists.txt

# Build and Install to a specific temporary directory
WORKDIR /src/build
RUN cmake .. \
        -DCMAKE_BUILD_TYPE=Release \
        -DBUILD_PLUGINS=ON \
        -DBUILD_SIMPLESTREAM=ON && \
    make -j$(nproc) && \
    mkdir -p /newroot && \
    make DESTDIR=/newroot install

# Stage 2 - Runtime image
FROM ubuntu:24.04

# Install runtime dependencies
RUN apt-get update && \
    apt-get -y upgrade && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install --no-install-recommends -y \
        ca-certificates \
        curl \
        fdkaac \
        gr-funcube \
        gr-iqbal \
        libairspyhf1 \
        libboost-chrono1.83.0t64 \
        libboost-log1.83.0 \
        libfreesrp0 \
        libgnuradio-analog3.10.9t64 \
        libgnuradio-digital3.10.9t64 \
        libgnuradio-filter3.10.9t64 \
        libgnuradio-network3.10.9t64 \
        libgnuradio-osmosdr0.2.0t64 \
        libgnuradio-uhd3.10.9t64 \
        libsoapysdr0.8 \
        librtlsdr2 \
        libxtrx0 \
        soapysdr0.8-module-all \
        sox \
        wget \
        python3-requests \
        python3-six \
        dos2unix \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /usr/share/{doc,man,info} /usr/local/share/{doc,man,info}

# --- THE FIX: Copy from the /newroot path in the builder stage ---
COPY --from=builder /newroot /

# Fix the error message level for SmartNet
RUN mkdir -p /etc/gnuradio/conf.d/ && \
    echo 'log_level = info' >> /etc/gnuradio/conf.d/gnuradio-runtime.conf && \
    ldconfig

# Runtime setup
WORKDIR /app
RUN mkdir -p /data/configs /data/logs

# GNURadio requires a place to store some files
ENV HOME=/tmp

# --- MONITORING & ENTRYPOINT ---
COPY trunk-recorder/entrypoint.sh /entrypoint.sh
COPY trunk-recorder/monitor.py /app/monitor.py
COPY trunk-recorder/configure.py /app/configure.py
COPY configs/trunk-recorder.json /app/default-config.json

# --- CRITICAL FIX: Remove the shadow config file ---
# This ensures trunk-recorder is forced to look at the /data folder for its config
RUN rm -f /app/config.json /usr/local/etc/trunk-recorder/config.json

RUN dos2unix /entrypoint.sh /app/monitor.py /app/configure.py && \
    chmod +x /entrypoint.sh /app/monitor.py /app/configure.py

ENTRYPOINT ["/entrypoint.sh"]

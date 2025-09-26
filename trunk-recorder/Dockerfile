# syntax=docker/dockerfile:1
FROM ubuntu:24.04 AS builder

# Install base build tools (changes rarely)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install --no-install-recommends -y \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        git \
        pkg-config \
        wget \
        python3-six

# Install GNU Radio and SDR libraries (changes rarely)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install --no-install-recommends -y \
        gnuradio-dev \
        gr-osmosdr \
        libosmosdr-dev

# Install SDR hardware libraries (changes rarely)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install --no-install-recommends -y \
        libairspy-dev \
        libairspyhf-dev \
        libfreesrp-dev \
        libhackrf-dev \
        librtlsdr-dev \
        libuhd-dev \
        libusb-dev \
        libusb-1.0-0-dev \
        libsoapysdr-dev

# Install additional libraries (changes rarely)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install --no-install-recommends -y \
        libboost-all-dev \
        libcurl4-openssl-dev \
        libgmp-dev \
        liborc-0.4-dev \
        libpthread-stubs0-dev \
        libsndfile1-dev \
        libssl-dev \
        ffmpeg

# Clone source code (changes when trunk-recorder updates)
WORKDIR /src
RUN git clone --depth 1 https://github.com/TrunkRecorder/trunk-recorder.git .

# Build trunk-recorder with cache mount for build artifacts
WORKDIR /src/build
RUN --mount=type=cache,target=/src/build,sharing=locked \
    cmake .. && \
    make -j$(nproc) && \
    make DESTDIR=/newroot install

# Stage 2 - Runtime image
FROM ubuntu:24.04

# Install runtime dependencies (simplified to avoid cache mount issues)
RUN apt-get update && \
    apt-get -y upgrade && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install --no-install-recommends -y \
        ca-certificates \
        curl \
        wget \
        sox \
        fdkaac \
        gr-funcube \
        gr-iqbal \
        libboost-log1.83.0 \
        libboost-chrono1.83.0t64 \
        libsoapysdr0.8 \
        soapysdr0.8-module-all \
        librtlsdr-dev \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /usr/share/{doc,man,info} /usr/local/share/{doc,man,info}

COPY --from=builder /newroot /

# Fix the error message level for SmartNet
RUN mkdir -p /etc/gnuradio/conf.d/ && \
    echo 'log_level = info' >> /etc/gnuradio/conf.d/gnuradio-runtime.conf && \
    ldconfig

# runtime setup
WORKDIR /app
RUN mkdir -p /data/configs /data/logs

# GNURadio requires a place to store some files, can only be set via $HOME env var.
ENV HOME=/tmp

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
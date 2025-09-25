FROM ubuntu:24.04 AS builder

# Install dependencies for building trunk-recorder
RUN apt-get update && \
    apt-get -y upgrade && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get install --no-install-recommends -y \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        git \
        gnuradio-dev \
        gr-osmosdr \
        libosmosdr-dev \
        libairspy-dev \
        libairspyhf-dev \
        libbladerf-dev \
        libboost-all-dev \
        libcurl4-openssl-dev \
        libfreesrp-dev \
        libgmp-dev \
        libhackrf-dev \
        libmirisdr-dev \
        liborc-0.4-dev \
        libpthread-stubs0-dev \
        librtlsdr-dev \
        libsndfile1-dev \
        libsoapysdr-dev \
        libssl-dev \
        libuhd-dev \
        libusb-dev \
        libusb-1.0-0-dev \
        libxtrx-dev \
        pkg-config \
        wget \
        python3-six \
        ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone --depth 1 https://github.com/TrunkRecorder/trunk-recorder.git .
WORKDIR /src/build
RUN cmake .. && make -j$(nproc) && make DESTDIR=/newroot install

# Stage 2 - Runtime image
FROM ubuntu:24.04
RUN apt-get update && apt-get -y upgrade && apt-get install --no-install-recommends -y \
    ca-certificates \
    gr-funcube \
    gr-iqbal \
    curl \
    wget \
    libboost-log1.83.0 \
    libboost-chrono1.83.0t64 \
    libgnuradio-digital3.10.9t64 \
    libgnuradio-analog3.10.9t64 \
    libgnuradio-filter3.10.9t64 \
    libgnuradio-network3.10.9t64 \
    libgnuradio-uhd3.10.9t64 \
    libgnuradio-osmosdr0.2.0t64 \
    libsoapysdr0.8 \
    soapysdr0.8-module-all \
    libairspyhf1 \
    libfreesrp0 \
    librtlsdr2 \
    libxtrx0 \
    sox \
    fdkaac \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /usr/share/{doc,man,info} \
 && rm -rf /usr/local/share/{doc,man,info}

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
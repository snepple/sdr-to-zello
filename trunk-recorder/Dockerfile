# Stage 1 - Build Stage
FROM ubuntu:24.04 AS builder

# ... [Keep your existing Stage 1 / Builder code here] ...
# (No changes needed to the builder section)

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

# Copy the built binary from Stage 1
COPY --from=builder /newroot /

# Fix the error message level for SmartNet
RUN mkdir -p /etc/gnuradio/conf.d/ && \
    echo 'log_level = info' >> /etc/gnuradio/conf.d/gnuradio-runtime.conf && \
    ldconfig

# Runtime setup
WORKDIR /app
RUN mkdir -p /data/configs /data/logs

# GNURadio requires a place to store some files, can only be set via $HOME env var.
ENV HOME=/tmp

# --- UPDATED SECTION FOR MONITORING & ENTRYPOINT ---
COPY trunk-recorder/entrypoint.sh /entrypoint.sh
COPY trunk-recorder/monitor.py /app/monitor.py
COPY trunk-recorder/configure.py /app/configure.py
COPY configs/trunk-recorder.json /app/default-config.json

# CRITICAL: Clean up line endings from Windows and make scripts executable
RUN dos2unix /entrypoint.sh /app/monitor.py /app/configure.py && \
    chmod +x /entrypoint.sh /app/monitor.py /app/configure.py

# Set the entrypoint as the starting instruction
ENTRYPOINT ["/entrypoint.sh"]

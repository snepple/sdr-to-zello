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
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /usr/share/{doc,man,info} /usr/local/share/{doc,man,info}

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

# --- ADDED SECTION FOR DYNAMIC SERIAL NUMBER ---
# Copy the injection script and configuration template
COPY trunk-recorder/start_trunk.sh /app/start_trunk.sh
COPY configs/trunk-recorder.json /data/configs/trunk-recorder.json
RUN chmod +x /app/start_trunk.sh

# We override the previous ENTRYPOINT to use our new script
ENTRYPOINT ["/app/start_trunk.sh"]

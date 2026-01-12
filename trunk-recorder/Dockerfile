# Stage 2 - Runtime image
FROM ubuntu:24.04

# ... [Keep your previous apt-get install and runtime dependency layers here] ...

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

# --- UPDATED SECTION FOR MERGED ENTRYPOINT ---
# Copy the merged entrypoint script and the default configuration template
COPY trunk-recorder/entrypoint.sh /entrypoint.sh
COPY configs/trunk-recorder.json /app/default-config.json
COPY trunk-recorder/configure.py /app/configure.py

# Ensure the entrypoint is executable
RUN chmod +x /entrypoint.sh

# Set the merged entrypoint as the starting instruction
ENTRYPOINT ["/entrypoint.sh"]

# Base image
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    iproute2 \
    dpkg \
	ca-certificates \
    apt-utils \
	qbittorrent-nox \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app

# Fetch the latest ExpressVPN version dynamically
RUN chmod +x /app/download_expressvpn.sh
RUN /app/download_expressvpn.sh

# Copy entrypoint script
RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Expose necessary ports
EXPOSE 8000


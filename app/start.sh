#!/bin/bash
set -e

chown -R ${PUID}:${PGID} /mnt/movies
chown -R ${PUID}:${PGID} /mnt/tv

# Start qBittorrent in the background
echo "Starting qBittorrent..."
qbittorrent-nox &

# Start the FastAPI app in the foreground
echo "Starting FastAPI app..."
exec uvicorn app:app --host 0.0.0.0 --port 8000

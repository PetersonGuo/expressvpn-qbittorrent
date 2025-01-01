#!/bin/bash
set -e

# Start ExpressVPN
if ! command -v expressvpn &> /dev/null; then
  echo "Error: ExpressVPN is not installed or not in PATH."
  exit 1
fi

if [[ -z "$EXPRESSVPN_ACTIVATION_CODE" ]]; then
  echo "Error: EXPRESSVPN_ACTIVATION_CODE is not set."
  exit 1
fi

echo "Activating ExpressVPN..."
expressvpn activate "$EXPRESSVPN_ACTIVATION_CODE" --noninteractive || {
  echo "Error: Failed to activate ExpressVPN."
  exit 1
}

expressvpn preferences set network_lock on
expressvpn connect || {
  echo "Error: Failed to connect ExpressVPN."
  exit 1
}

# Start qBittorrent
echo "Starting qBittorrent..."
qbittorrent-nox &

# Start your main application
exec "$@"

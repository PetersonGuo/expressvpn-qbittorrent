#!/bin/bash
set -e

# Start expressvpnd daemon
echo "Starting expressvpnd daemon..."
service expressvpn start || {
    echo "Failed to start expressvpnd daemon."
    exit 1
}

# Activate ExpressVPN
if [ -n "$EXPRESSVPN_ACTIVATION_CODE" ]; then
    echo "Activating ExpressVPN..."
    echo "$EXPRESSVPN_ACTIVATION_CODE" | expressvpn activate --noninteractive
    expressvpn preferences set network_lock on
    expressvpn connect
else
    echo "ExpressVPN activation code not found."
    exit 1
fi

# Keep the container running
exec "$@"

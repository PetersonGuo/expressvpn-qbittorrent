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
    /usr/bin/expect /app/activate.ex
	expressvpn preferences set block_malicious true
	expressvpn preferences set block_ads true
	expressvpn preferences set block_adult true
	expressvpn preferences set send_diagnostics false
	expressvpn protocol lightway_udp

	# Enable network lock
	echo "Enabling network lock..."
	if ! expressvpn preferences set network_lock on; then
		echo "Network lock not available. Continuing without it."
	fi
    expressvpn connect smart
else
    echo "ExpressVPN activation code not found."
    exit 1
fi

# Start the FastAPI app
echo "Starting FastAPI application..."
exec uvicorn app:app --host 0.0.0.0 --port 8000# Keep the container running

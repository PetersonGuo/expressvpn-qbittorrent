#!/bin/bash
set -e

# Debugging: Log each step
set -x

# Base URL for ExpressVPN downloads
base_url="https://www.expressvpn.com/latest#linux"

# Check if required tools are available
command -v curl >/dev/null 2>&1 || { echo "Error: curl is not installed. Exiting."; exit 1; }
command -v dpkg >/dev/null 2>&1 || { echo "Error: dpkg is not installed. Exiting."; exit 1; }

# Fetch the latest version dynamically from the ExpressVPN website
echo "Fetching ExpressVPN download page..."
html=$(curl -s "$base_url")
echo "Page content fetched successfully."

# Save the HTML for debugging
echo "$html" > /tmp/expressvpn.html

# Extract the download URL
latest_url=$(echo "$html" | grep -o 'https://www\.expressvpn\.works/clients/linux/expressvpn_[^"]*\.deb' | head -n 1)

# Validate the extracted URL
if [[ -z "$latest_url" ]]; then
  echo "Error: Unable to find the latest ExpressVPN download URL."
  exit 1
fi

# Extract the file name from the URL
file_name=$(basename "$latest_url")

# Download the latest version
echo "Downloading ExpressVPN from: $latest_url"
curl -O "$latest_url" || { echo "Error: Failed to download ExpressVPN package. Exiting."; exit 1; }

# Install the downloaded .deb file
echo "Installing ExpressVPN package: $file_name"
dpkg -i "$file_name" || apt-get install -f -y || { echo "Error: Failed to install ExpressVPN. Exiting."; exit 1; }

# Clean up
echo "Cleaning up downloaded package: $file_name"
rm -f "$file_name"

echo "ExpressVPN installation completed successfully!"

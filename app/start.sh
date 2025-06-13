#!/usr/bin/env bash
set -e

CONFIG_DIR=/config/qBittorrent
CONF_FILE=$CONFIG_DIR/qBittorrent.conf
SRC_CONF=/app/qBittorrent.conf

SALT=$(python3 - << 'PYCODE'
import os, base64
print(base64.b64encode(os.urandom(16)).decode())
PYCODE
)

HASH=$(python3 - "$QBT_PASSWORD" "$SALT" << 'PYCODE'
import sys, hashlib, base64
pw = sys.argv[1].encode()
salt = base64.b64decode(sys.argv[2])
dk = hashlib.pbkdf2_hmac('sha512', pw, salt, 100000, dklen=64)
print(base64.b64encode(dk).decode())
PYCODE
)

if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
    cp "$SRC_CONF" "$CONF_FILE"
fi

if ! grep -q 'WebUI\\Password_PBKDF2=' "$CONF_FILE"; then
    echo "⚙️  Setting qBittorrent WebUI credentials..."
    cat >> "$CONF_FILE" <<EOF

[Preferences]
WebUI\\Username=${QBT_USERNAME}
WebUI\\Password_PBKDF2="@ByteArray(${SALT}:${HASH})"
EOF
fi

WEBUI_PORT=${WEBUI_PORT:-3000}

# Start the FastAPI app
echo "▶️  Starting FastAPI on :$WEBUI_PORT..."
exec uvicorn app:app --host 0.0.0.0 --port $WEBUI_PORT

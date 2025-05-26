# Base image
FROM python:3.13.3-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    expect \
    curl \
    qbittorrent-nox \
    wget \
    unzip \
    gnupg \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc-s1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    rustc \
    cargo \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# Install Rust using rustup
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && \
    ~/.cargo/bin/rustup default stable && \
    ~/.cargo/bin/rustup update && \
    echo 'export PATH=$PATH:$HOME/.cargo/bin' >> ~/.bashrc && \
    export PATH=$PATH:$HOME/.cargo/bin

# Copy application code
COPY . /app
WORKDIR /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy qBittorrent configuration
COPY qBittorrent.conf /root/.config/qBittorrent/qBittorrent.conf

# Add WebUI credentials to configuration
RUN echo -e "[Preferences]\nWebUI/Username=${QBT_USERNAME}\nWebUI/Password_ha1=$(echo -n ${QBT_PASSWORD} | sha1sum | awk '{print $1}')" > /root/.config/qBittorrent/qBittorrent.conf

# Make the start script executable
RUN chmod +x /app/start.sh

# Set default command
CMD ["/app/start.sh"]


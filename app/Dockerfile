# Base image
FROM python:3.13.4-slim

# Copy application code
COPY . /app
WORKDIR /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Make the start script executable
RUN chmod +x /app/start.sh

# Set default command
CMD ["/app/start.sh"]


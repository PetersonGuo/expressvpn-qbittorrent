# Base image
FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    qbittorrent-nox \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Start the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

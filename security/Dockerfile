# dLNk Security Service Dockerfile
FROM python:3.11-slim

LABEL maintainer="dLNk Team"
LABEL description="dLNk Security Service - Prompt Filter, Anomaly Detection, Alerts"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p /logs /data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DLNK_SECURITY_HOST=0.0.0.0
ENV DLNK_SECURITY_PORT=8089
ENV DLNK_LOG_LEVEL=INFO

# Expose port
EXPOSE 8089

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8089/health || exit 1

# Run the application
CMD ["python", "main.py"]

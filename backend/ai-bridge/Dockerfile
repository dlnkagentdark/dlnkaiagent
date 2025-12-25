# dLNk AI Bridge Dockerfile
FROM python:3.11-slim

LABEL maintainer="dLNk Team"
LABEL description="dLNk AI Bridge - Antigravity/Jetski gRPC Client"
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
RUN mkdir -p /logs /tokens

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DLNK_WS_HOST=0.0.0.0
ENV DLNK_WS_PORT=8765
ENV DLNK_REST_HOST=0.0.0.0
ENV DLNK_REST_PORT=8766
ENV DLNK_LOG_LEVEL=INFO

# Expose ports
EXPOSE 8765 8766

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8766/health || exit 1

# Run the application
CMD ["python", "main.py"]

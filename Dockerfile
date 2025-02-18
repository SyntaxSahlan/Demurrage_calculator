FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user and switch to it
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8006

# Configure environment variables with defaults
ENV PORT=8006 \
    WORKERS=4 \
    LOG_LEVEL=INFO \
    MAX_REQUESTS=10000

# Start with better worker configuration and logging
CMD uvicorn api:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers $WORKERS \
    --log-level $LOG_LEVEL \
    --limit-max-requests $MAX_REQUESTS \
    --proxy-headers \
    --access-log

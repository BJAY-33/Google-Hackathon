# Enhanced Agent Engine - Docker Configuration
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs temp test-results

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV WEB_HOST=0.0.0.0
ENV WEB_PORT=8080

# Expose the web interface port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash agent_user && \
    chown -R agent_user:agent_user /app
USER agent_user

# Start the web interface
CMD ["python", "web_main.py"]

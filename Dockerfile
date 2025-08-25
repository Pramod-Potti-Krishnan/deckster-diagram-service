# Diagram Microservice v2 - Docker Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for matplotlib and other packages
# Also install Node.js, npm for Mermaid CLI, and Chromium browser
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    curl \
    # Install Chromium browser and dependencies
    chromium \
    chromium-driver \
    # Additional dependencies for puppeteer
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set puppeteer to use system Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Install Mermaid CLI after setting environment variables
RUN npm install -g @mermaid-js/mermaid-cli@10.6.1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Note: templates directory already exists from COPY command
# Don't create it again as it would overwrite the copied templates!

# Railway provides PORT dynamically
EXPOSE ${PORT:-8001}

# Health check (uses PORT env var)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, httpx; port=os.getenv('PORT', '8001'); httpx.get(f'http://localhost:{port}/health')" || exit 1

# Environment variables (Railway will override PORT)
ENV WS_HOST=0.0.0.0
ENV WS_PORT=${PORT:-8001}
ENV LOG_LEVEL=INFO
ENV CACHE_TYPE=memory

# Run the application
CMD ["python", "main.py"]
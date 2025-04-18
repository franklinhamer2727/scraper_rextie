FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create and set permissions for directories
RUN mkdir -p data logs scraper && \
    chmod -R 777 data logs scraper

# Create and switch to non-root user
RUN useradd -m myuser && chown -R myuser:myuser /app
USER myuser

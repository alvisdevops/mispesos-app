FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only application code (not Dockerfile, etc.)
COPY app/ ./app/

# Create necessary directories
RUN mkdir -p temp logs

# Run the bot using module syntax for proper imports
CMD ["python", "-m", "app.main"]
# Docker configuration for Portable Offline AI Document Reader
# Build: docker build -t ai-doc-reader .
# Run: docker run -p 5000:5000 -v $(pwd)/data:/app/data ai-doc-reader
# Run with GPU: docker run --gpus all -p 5000:5000 -v $(pwd)/data:/app/data ai-doc-reader

FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    libjasper-dev \
    libtiff-dev \
    libharfbuzz0b \
    libwebp6 \
    libjasper1 \
    libopenjp2-7 \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    gfortran \
    tesseract-ocr \
    libtesseract-dev \
    libopencv-dev \
    libcamera-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p data logs uploads images && \
    chmod 755 data logs uploads images

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Expose API port
EXPOSE 5000

# Run application
CMD ["python3", "app.py", "api"]

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including poppler-utils
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-pip \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to run the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

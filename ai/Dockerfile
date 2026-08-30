FROM python:3.12-slim

# Install system dependencies (libgl1, libglib2.0-0 for OpenCV headless, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install lightweight CPU-only PyTorch first, followed by requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch torchvision && \
    pip install --no-cache-dir -r requirements.txt

# Copy AI source code and entrypoint
COPY . /app/ai
COPY entrypoint.sh /app/entrypoint.sh

# Ensure proper permissions
RUN mkdir -p /app/data /app/models && \
    chmod +x /app/entrypoint.sh && \
    chown -R appuser:appuser /app

USER appuser

ENV PYTHONPATH=/app

ENTRYPOINT ["/app/entrypoint.sh"]

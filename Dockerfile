FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH="/app"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies first for caching
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy application code
COPY . .

# Ensure start script has executable permissions
RUN chmod +x start.sh

# Expose Streamlit (8501) and FastAPI (8000)
EXPOSE 8501 8000

# Healthcheck targeting FastAPI
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

ENTRYPOINT ["./start.sh"]


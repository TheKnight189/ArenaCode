FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user 'appuser' (UID 1000)
RUN useradd -u 1000 -m -s /bin/bash appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

# Ensure app directory permissions
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

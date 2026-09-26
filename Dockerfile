# Single stage - install dependencies directly
FROM python:3.13-slim

WORKDIR /app

# Install build + runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy all project files
COPY . ./

# Install poetry and dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Install the local shifttestex package
RUN pip install -e .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/docs', timeout=5)" || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "shifttestex.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

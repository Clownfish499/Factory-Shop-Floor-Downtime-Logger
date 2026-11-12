# Production-capable Dockerfile for Factory Shop-Floor Execution System
# Note: Docker status is NOT VERIFIED in the current environment because Docker is not installed on the host.

FROM python:3.11-slim

# Create a non-root application group and user for container security
RUN groupadd -r shopfloor && useradd -r -g shopfloor -m -d /app shopfloor

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    DATABASE_PATH=/app/data/factory.db

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application files
COPY . .

# Create persistent database folder and set ownership to non-root user
RUN mkdir -p /app/data && chown -R shopfloor:shopfloor /app

USER shopfloor

# Volume mount point for persistent SQLite database
VOLUME ["/app/data"]

EXPOSE 5000

# Health check using python urllib
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; resp = urllib.request.urlopen('http://127.0.0.1:5000/health'); exit(0 if resp.status == 200 else 1)"

# Production execution using Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "app:create_app()"]

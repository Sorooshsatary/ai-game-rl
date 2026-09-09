# ==========================================
# Dockerfile for RL Game Platform
# Python 3.11 Slim Image
# ==========================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000

# Set working directory
WORKDIR /app

# Install dependencies first (leverages Docker cache layer)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/

# Expose web server port
EXPOSE 8000

# Health check to ensure service availability
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/config')" || exit 1

# Start the application server
CMD ["python", "run_server.py"]

FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set Python Path to include the src directory
ENV PYTHONPATH=/app

EXPOSE 8000

# --workers 1   : single worker prevents SSE stream fragmentation across processes
# --http h11    : forces the pure-Python H11 HTTP parser instead of httptools.
#                 httptools can buffer response bodies before flushing; h11 sends
#                 each chunk immediately, which is required for SSE to work through
#                 Cloudflare and Render proxies without triggering 20-second timeouts.
# --proxy-headers: trust X-Forwarded-* headers from Render's edge layer
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--workers", "1", "--proxy-headers", "--http", "h11"]

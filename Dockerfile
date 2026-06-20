FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set Python Path to include the src directory
ENV PYTHONPATH=/app

EXPOSE 8000

# We switch to Gunicorn with UvicornWorker for better stability on Render.
# --worker-class uvicorn.workers.UvicornWorker : Bridge between Gunicorn and FastAPI
# --timeout 0 : Disable worker timeouts to allow long-lived SSE connections
# --keep-alive 5 : Keep TCP connections open for proxies
# --threads 4 : Allow concurrent handling within a worker
CMD ["gunicorn", "src.main:app", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "0", "--keep-alive", "5", "--proxy-protocol", "--forwarded-allow-ips", "*"]

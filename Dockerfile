FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set Python Path to include the src directory
ENV PYTHONPATH=/app

EXPOSE 8000

# Reduced to 1 worker to ensure SSE streams are not buffered or fragmented by worker management
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "uvloop", "--workers", "1", "--proxy-headers"]

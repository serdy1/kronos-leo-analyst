FROM python:3.10-slim

WORKDIR /app

# Install git and essential build tools for potential C-extensions
RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set Python Path to include the src directory
ENV PYTHONPATH=/app/src:/app

# Hugging Face Spaces default port is 7860
EXPOSE 7860

# We use a CMD that respects the PORT env var provided by the platform, 
# defaulting to 7860 for Hugging Face compatibility.
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-7860} --http h11"]

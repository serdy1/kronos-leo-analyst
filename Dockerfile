FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set Python Path to include the src directory
ENV PYTHONPATH=/app

EXPOSE 8000

# FastMCP run command with stateless_http=True
# This is the most robust way to run MCP on Render Free Tier.
# It automatically handles the SSE endpoint and headers correctly.
CMD ["python", "src/main.py"]

FROM python:3.11-slim

WORKDIR /app

# Install build tools and dependencies for pymupdf, on ARM architectures
RUN apt-get update && \
    apt-get install -y build-essential gcc pkg-config python3-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--loop", "asyncio", "--reload", "--host", "0.0.0.0", "--port", "8000"]

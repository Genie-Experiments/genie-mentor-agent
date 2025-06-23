FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# cache pip dependencies to BuildKit's internal cache store
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# remove image's pip cache to reduce image size
RUN rm -rf /root/.cache/pip

COPY src/ ./src/

COPY secrets/ ./secrets/

COPY ingestion_state/ ./ingestion_state/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"]

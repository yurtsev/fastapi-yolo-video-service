FROM python:3.12-slim AS builder
WORKDIR /backend

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
            gcc \
            libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv && uv pip install --editable . --system

FROM python:3.12-slim
WORKDIR /backend

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local

COPY src src
COPY yolov8n.pt .
COPY .env .

CMD ["python", "-m", "src.main"]
# Stage 1: Build Frontend
FROM node:22.8.0-alpine3.19 AS frontend-builder

WORKDIR /app/frontend

COPY frontend/unspoken/package*.json ./

RUN npm install && npm install typescript -g

COPY frontend/unspoken .

ARG PORT
ENV VITE_API_PORT ${PORT:-80}

ARG CACHE_BUST=1

RUN npm run build

# Stage 2: Pin uv toolchain
FROM ghcr.io/astral-sh/uv:0.10.2 AS uv-bin

# Stage 3: Build Backend and Final Image
FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu22.04

ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV DEBIAN_FRONTEND noninteractive
ENV UV_PYTHON=3.12
ENV UV_MANAGED_PYTHON=1

# Install system dependencies
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libavcodec-extra \
    gcc \
    python3-dev \
    libffi-dev \
    python3-pip \
    libmagic-dev \
    libblas3 \
    liblapack3 \
    liblapack-dev \
    libblas-dev \
    nodejs \
    npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=uv-bin /uv /bin/uv

WORKDIR /app

# Copy and install Python dependencies
COPY pyproject.toml uv.lock ./
RUN --network=host --mount=type=cache,target=/root/.cache/uv \
    sh -c 'for attempt in 1 2 3 4 5; do \
        uv sync -vv --python 3.12 --managed-python --frozen --no-dev --no-install-project && exit 0; \
        echo "uv sync failed (attempt ${attempt}/5), retrying in $((attempt * 5))s..."; \
        sleep $((attempt * 5)); \
    done; \
    echo "uv sync failed after 5 attempts"; \
    exit 1'

# Copy backend code
COPY . .

# Install Python dependencies
RUN --network=host --mount=type=cache,target=/root/.cache/uv \
    sh -c 'for attempt in 1 2 3 4 5; do \
        uv sync -vv --python 3.12 --managed-python --frozen --no-dev && exit 0; \
        echo "uv sync failed (attempt ${attempt}/5), retrying in $((attempt * 5))s..."; \
        sleep $((attempt * 5)); \
    done; \
    echo "uv sync failed after 5 attempts"; \
    exit 1'

# Copy built frontend from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose the FastAPI port
EXPOSE ${PORT:-80}

CMD ["/bin/sh", "-c", "uv run --python 3.12 --managed-python --no-sync --no-dev --locked gunicorn unspoken.app:app -w 1 -b ${HOST:-0.0.0.0}:${PORT:-80} -k uvicorn.workers.UvicornWorker"]

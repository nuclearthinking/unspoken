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

# Stage 2: Build Backend and Final Image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

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

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy and install Python dependencies without project
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync -vv --frozen --no-dev --no-install-project 

# Copy backend code
COPY . .

# Install Python dependencies with project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync -vv --frozen --no-dev

# Copy built frontend from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose the FastAPI port
EXPOSE ${PORT:-80}

CMD ["/bin/sh", "-c", "uv run gunicorn unspoken.app:app -w 2 -b ${HOST:-0.0.0.0}:${PORT:-80} -k uvicorn.workers.UvicornWorker"]

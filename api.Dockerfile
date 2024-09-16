FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

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
    libblas-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync -vv --frozen --no-dev --no-install-project 

ADD . /app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync -vv --frozen --no-dev

EXPOSE 8000
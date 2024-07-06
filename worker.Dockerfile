FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
LABEL authors="nuclearthinking"

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

RUN pip install -U pip && pip install poetry

WORKDIR /app

COPY ["pyproject.toml", "poetry.lock", "README.md", "/app/"]

RUN poetry config virtualenvs.create false && \
    poetry install --without api,dev --no-interaction --no-ansi --no-root

COPY . /app/


FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
LABEL authors="nuclearthinking"

ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

RUN apt update && \
    apt -y upgrade && \
    apt install -y ffmpeg libavcodec-extra gcc python3-dev libffi-dev python3-pip libmagic-dev libblas3 liblapack3 liblapack-dev libblas-dev

RUN pip install -U pip && pip install poetry

WORKDIR /app

COPY ["pyproject.toml", "poetry.lock", "README.md", "/app/"]

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

COPY . /app/


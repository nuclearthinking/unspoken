FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
LABEL authors="nuclearthinking"

RUN apt update && \
    apt -y upgrade && \
    apt install -y --no-install-recommends \
    libmagic-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -U pip && pip install poetry

WORKDIR /app

COPY ["pyproject.toml", "poetry.lock", "README.md", "/app/"]

RUN poetry config virtualenvs.create false && \
    poetry install --without worker,dev --no-interaction --no-ansi --no-root

COPY . /app/

EXPOSE 8000
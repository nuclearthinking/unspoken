# UNSPOKEN

Convert audio to text-conversation separated by speakers.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Building the Frontend (Optional)](#building-the-frontend-optional)
- [Contributing](#contributing)

## Introduction

UNSPOKEN converts audio files to text conversations, labeled by speakers, using `faster-whisper` and `pyanote.audio`
diarization.

## Features

- Audio to text conversion
- Speaker diarization
- API and optional UI

## Prerequisites

- NVIDIA drivers installed

## Installation

1. Clone repository:
    ```bash
    git clone https://github.com/nuclearthinking/unspoken.git
    cd unspoken
    ```
2. Build and run application with script:
    ```bash
    chmod +x deploy.sh # make file executable
    ./deploy.sh 
    ```

![img_1.png](docs/img_1.png)
![img_2.png](docs/img_2.png)

## Usage

1. **Upload an Audio File**:
    ```bash
    curl --location 'http://0.0.0.0:8000/upload/audio' --form 'file=@"/path/to/audio_file.m4a"'
    ```
2. **Check Task Status**:
    ```bash
    curl --location 'http://0.0.0.0:8000/task/{task_id}'
    ```
   **Response**:
    ```json
    {
      "id": 21,
      "status": "completed",
      "file_name": "file_name",
      "speakers": ["speaker_0", "speaker_1"],
      "messages": [
        {"start": 0.0, "end": 3.62, "text": "Message 1", "speaker": "speaker_0"},
        {"start": 6.96, "end": 15.0, "text": "Message 2", "speaker": "speaker_1"}
      ]
    }
    ```

## Building the Frontend (Optional)

1. **Install Dependencies**:
    ```bash
    cd frontend/unspoken
    npm install
    ```
2. **Build Frontend**:
    ```bash
    npm run build
    ```
3. **Run Frontend**:
    ```bash
    docker-compose --profile frontend up
    ```

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details.
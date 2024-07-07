from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    # WHISPER SETTINGS
    whisper_model: str = 'large-v3'
    device: str = 'cuda'
    device_index: int = 0
    compute_type: str = 'auto'

    # HUGGINGFACE SETTINGS
    hf_token: str

    # DB SETTINGS
    db_host: str = '0.0.0.0'
    db_port: int = 5432
    db_name: str = 'unspoken'
    db_user: str
    db_password: str

    # RABBITMQ SETTINGS
    rabbitmq_host: str = '0.0.0.0'
    rabbitmq_port: int = 5672
    rabbitmq_vhost: str = '/'
    rabbitmq_user: str
    rabbitmq_password: str
    transcribe_audio_queue: str = 'transcribe_audio'
    transcribe_audio_routing_key: str = 'transcribe.#'

    # OTHER SETTINGS
    temp_files_dir: str = 'temp_files'
    alembic_ini_path: str = 'alembic.ini'


settings = _Settings()

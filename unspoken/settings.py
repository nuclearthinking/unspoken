from pydantic import BaseSettings


class _Settings(BaseSettings):
    # MODEL SETTINGS
    whisper_model: str = 'openai/whisper-large-v3'
    device: str = 'cuda'
    device_index: int = 0
    compute_type: str = 'float16'

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


settings = _Settings()

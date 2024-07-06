from pydantic_settings import BaseSettings

from unspoken.enitites.enums.nemo_type import NemoDomainType


class _Settings(BaseSettings):
    # WHISPER SETTINGS
    whisper_model: str = 'large-v2'
    device: str = 'cuda'
    device_index: int = 0
    compute_type: str = 'auto'

    # HUGGINGFACE SETTINGS
    hf_token: str

    # NEMO SETTINGS
    nemo_domain_type: NemoDomainType = NemoDomainType.telephonic

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


settings = _Settings()

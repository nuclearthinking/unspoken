from pydantic import BaseSettings

from unspoken.enitites.enums.nemo_type import NemoDomainType


class _Settings(BaseSettings):
    # WHISPER SETTINGS
    whisper_model: str = 'large-v2'
    device: str = 'cuda'
    device_index: int = 0
    compute_type: str = 'float8'

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
    high_resource_demand_queue: str = 'high_resource_demand'
    high_resource_demand_routing_key: str = 'high.#'
    low_resource_demand_queue: str = 'low_resource_demand'
    low_resource_demand_routing_key: str = 'low.#'

    # OTHER SETTINGS
    temp_files_dir: str = 'temp_files'


settings = _Settings()

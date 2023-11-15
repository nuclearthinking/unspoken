from pydantic_settings import BaseSettings


class _Settings(BaseSettings):
    # MODEL SETTINGS
    whisper_model: str = "openai/whisper-large-v3"
    device: str = 'cuda'
    device_index: int = 0
    compute_type: str = 'float16'


settings = _Settings()

import dataclasses
import json
import logging
from pathlib import Path

from huggingface_hub import snapshot_download

from unspoken.enitites.enums.ml_models import Model
from unspoken.exceptions import ModelNotFound, UnspokenException
from unspoken.settings import settings

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class _ModelInfo:
    name: str
    repo_id: str
    revision: str


def _get_model_info(model_name: str) -> _ModelInfo:
    try:
        with open(settings.models_lock_path, 'r') as f:
            models = json.load(f)
            if model_name not in models:
                raise ModelNotFound(f'Model info for model {model_name} not found.')
            model_info = models[model_name]
            return _ModelInfo(name=model_name, **model_info)
    except json.JSONDecodeError as e:
        raise UnspokenException('Unable to read model_lock file.') from e


def load_model(model: Model):
    logger.info(f'Loading model {model.value}.')
    model_info = _get_model_info(model.value)
    model_path = model.path()
    if Path(model_path).exists():
        logger.info(f'Model {model.value} already exists, skipping.')
        return
    logger.info(f'Downloading model {model.value}.')
    snapshot_download(
        repo_id=model_info.repo_id,
        revision=model_info.revision,
        local_dir=model_path,
        local_dir_use_symlinks=False,
    )
    logger.info(f'Model {model.value} downloaded.')


def prepare_models():
    for model in Model:
        load_model(model)

import dataclasses
import json
import logging
import time
from pathlib import Path
from threading import Lock

from huggingface_hub import HfApi, snapshot_download

from unspoken.enitites.enums.ml_models import Model
from unspoken.exceptions import ModelNotFound, UnspokenException
from unspoken.settings import settings

logger = logging.getLogger(__name__)
_prepare_lock = Lock()
_models_prepared = False


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


def _collect_model_size(path: Path) -> tuple[int, float]:
    file_count = 0
    total_size = 0
    for file_path in path.rglob('*'):
        if file_path.is_file():
            file_count += 1
            total_size += file_path.stat().st_size
    return file_count, total_size / (1024 * 1024)


def _get_remote_files_count(repo_id: str, revision: str) -> int | None:
    try:
        model_info = HfApi(token=settings.hf_token).model_info(repo_id=repo_id, revision=revision)
        return len(model_info.siblings or [])
    except Exception:
        logger.warning(
            'Unable to fetch remote metadata for %s@%s. Download progress will only be available on completion.',
            repo_id,
            revision,
        )
        return None


def load_model(model: Model) -> bool:
    model_info = _get_model_info(model.value)
    model_path = Path(model.path())
    ready_marker = model_path / '.ready'

    logger.info('Model "%s": checking local cache at %s.', model.value, model_path)
    if model_path.exists() and ready_marker.exists():
        file_count, size_mb = _collect_model_size(model_path)
        logger.info(
            'Model "%s": already available locally (%s files, %.1f MiB).',
            model.value,
            file_count,
            size_mb,
        )
        return False
    if model_path.exists() and not ready_marker.exists():
        logger.warning(
            'Model "%s": cache directory exists but readiness marker is missing. Re-validating by re-downloading.',
            model.value,
        )

    expected_files = _get_remote_files_count(model_info.repo_id, model_info.revision)
    if expected_files is not None:
        logger.info(
            'Model "%s": downloading from %s@%s (%s files expected).',
            model.value,
            model_info.repo_id,
            model_info.revision,
            expected_files,
        )
    else:
        logger.info(
            'Model "%s": downloading from %s@%s.',
            model.value,
            model_info.repo_id,
            model_info.revision,
        )

    download_started_at = time.perf_counter()
    snapshot_download(
        repo_id=model_info.repo_id,
        revision=model_info.revision,
        local_dir=str(model_path),
        local_dir_use_symlinks=False,
        token=settings.hf_token,
    )
    elapsed_seconds = time.perf_counter() - download_started_at
    file_count, size_mb = _collect_model_size(model_path)
    ready_marker.write_text(f'{model_info.repo_id}@{model_info.revision}\n', encoding='utf-8')
    logger.info(
        'Model "%s": download finished in %.1fs (%s files, %.1f MiB).',
        model.value,
        elapsed_seconds,
        file_count,
        size_mb,
    )
    return True


def prepare_models(force: bool = False):
    global _models_prepared

    if _models_prepared and not force:
        logger.info('Model bootstrap skipped: models already prepared in this process.')
        return

    with _prepare_lock:
        if _models_prepared and not force:
            logger.info('Model bootstrap skipped: models already prepared in this process.')
            return

        started_at = time.perf_counter()
        downloaded_models = 0
        models = list(Model)
        total_models = len(models)

        logger.info('Model bootstrap started for %s models.', total_models)
        for index, model in enumerate(models, start=1):
            logger.info('Model bootstrap step %s/%s: %s', index, total_models, model.value)
            if load_model(model):
                downloaded_models += 1

        _models_prepared = True
        total_elapsed = time.perf_counter() - started_at
        logger.info(
            'Model bootstrap finished in %.1fs. Downloaded %s/%s models in this run.',
            total_elapsed,
            downloaded_models,
            total_models,
        )

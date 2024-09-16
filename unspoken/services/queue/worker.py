import logging

from celery.signals import worker_process_init

from unspoken.core.loader import prepare_models

from .broker import celery
from .tasks import transcribe

logger = logging.getLogger(__name__)

worker = celery
worker.register_task(transcribe)


@worker_process_init.connect
def configure_worker(**_):
    logger.info('Initializing worker.')
    prepare_models()
    logger.info('Initializing completed.')

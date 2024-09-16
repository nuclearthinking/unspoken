import logging

from celery import Celery
from kombu import Queue

from unspoken.settings import settings

logger = logging.getLogger(__name__)

broker_url = 'amqp://{user}:{password}@{host}:{port}{vhost}'.format(
    user=settings.rabbitmq_user,
    password=settings.rabbitmq_password,
    host=settings.rabbitmq_host,
    port=settings.rabbitmq_port,
    vhost=settings.rabbitmq_vhost,
)

celery = Celery('unspoken', broker=broker_url)
celery.conf.update(
    worker_hijack_root_logger=False,
)
celery.conf.task_queues = [
    Queue(
        settings.transcribe_audio_queue,
        routing_key=settings.transcribe_audio_routing_key,
    ),
]

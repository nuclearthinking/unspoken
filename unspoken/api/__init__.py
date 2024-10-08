from .messages import messages_router
from .speakers import speakers_router
from .tasks import tasks_router
from .tasks_v2 import tasks_router as tasks_router_v2
from .upload import upload_router

__all__ = [
    'messages_router',
    'speakers_router',
    'tasks_router',
    'tasks_router_v2',
    'upload_router',
]

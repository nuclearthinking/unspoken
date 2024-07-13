import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from unspoken.api import tasks_router, upload_router, messages_router, speakers_router, tasks_router_v2
from unspoken.settings import settings
from unspoken.services.db.base import setup as db_setup

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger('uvicorn')

app = FastAPI(debug=True, title='Unspoken')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['*'],
    allow_credentials=True,
)

app.include_router(tasks_router)
app.include_router(upload_router)
app.include_router(tasks_router_v2)
app.include_router(messages_router)
app.include_router(speakers_router)


def _init_temp_file_dir():
    logger.info('Initializing temp files directory')
    temp_file_dir_path = Path(settings.temp_files_dir)
    if not temp_file_dir_path.exists():
        logger.info('Temp files directory not found, creating')
        temp_file_dir_path.mkdir(parents=True, exist_ok=True)
    logger.info('Initializing temp files directory finished')


def _init_db():
    logger.info('Initializing database')
    db_setup()
    logger.info('Initializing database finished')


@app.on_event('startup')
async def startup_event():
    logger.info('Starting up')
    _init_db()
    _init_temp_file_dir()
    logger.info('Starting up finished')

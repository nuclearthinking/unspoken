import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from unspoken.api.tasks import tasks_router
from unspoken.api.upload import upload_router
from unspoken.services.db.base import setup as db_setup

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger('uvicorn')

app = FastAPI(debug=True)
app.include_router(tasks_router)
app.include_router(upload_router)

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


def init_db():
    logger.info('Initializing database')
    db_setup()
    logger.info('Initializing database finished')


@app.on_event('startup')
async def startup_event():
    logger.info('Starting up')
    init_db()
    logger.info('Starting up finished')

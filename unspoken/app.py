import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from unspoken.api import messages_router, speakers_router, tasks_router, tasks_router_v2, upload_router
from unspoken.services.db.base import setup as db_setup
from unspoken.services.ml.pipelines.transcribe_flow import transcribe_audio_flow
from unspoken.services.task_queue import start_worker, stop_worker
from unspoken.settings import settings

logging.basicConfig(
    level=logging.INFO,
)
logger = logging.getLogger('uvicorn')


worker_thread = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    _init_db()
    _init_temp_file_dir()
    global worker_thread
    worker_thread = start_worker(transcribe_audio_flow)
    yield
    stop_worker()
    if worker_thread:
        worker_thread.join()


app = FastAPI(debug=True, title='Unspoken', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['*'],
    allow_credentials=True,
)

app.include_router(tasks_router, prefix='/api')
app.include_router(upload_router, prefix='/api')
app.include_router(tasks_router_v2, prefix='/api')
app.include_router(messages_router, prefix='/api')
app.include_router(speakers_router, prefix='/api')

app.mount("/assets", StaticFiles(directory=Path(settings.frontend_build_path) / "assets"), name="static")

@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    if full_path.startswith("api/"):
        return await request.app.router(request.scope, request.receive, request.send)
    else:
        return FileResponse(Path(settings.frontend_build_path) / "index.html")

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

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import time
import logging

from app.api import jobs
from app.services.job_manager import job_manager
from app.services.cleanup_service import cleanup_loop
from app.config import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    job_manager.start_workers()
    cleanup_task = asyncio.create_task(cleanup_loop())
    yield
    # Shutdown
    cleanup_task.cancel()

app = FastAPI(title="ytmp3-backend", lifespan=lifespan)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"Request: {request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.4f}s"
    )
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

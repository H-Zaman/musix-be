from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

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

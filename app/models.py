from pydantic import BaseModel, HttpUrl
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid
import asyncio

class JobState(str, Enum):
    QUEUED = "queued"
    FETCHING_METADATA = "fetching_metadata"
    DOWNLOADING = "downloading"
    CONVERTING = "converting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobCreate(BaseModel):
    url: str

class JobStatusResponse(BaseModel):
    id: str
    status: str
    title: Optional[str] = None
    progress: float = 0.0
    speed: Optional[str] = None
    eta: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None
    download_url: Optional[str] = None

class Job:
    """Internal model for the in-memory job manager."""
    def __init__(self, url: str):
        self.id: str = str(uuid.uuid4())
        self.url: str = url
        self.status: JobState = JobState.QUEUED
        self.title: Optional[str] = None
        self.progress: float = 0.0
        self.speed: Optional[str] = None
        self.eta: Optional[str] = None
        self.filename: Optional[str] = None
        self.output_path: Optional[str] = None
        self.error: Optional[str] = None
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = datetime.utcnow()
        self.process: Optional[asyncio.subprocess.Process] = None
        self.cancellation_requested: bool = False

    def update(self):
        self.updated_at = datetime.utcnow()

    def to_response(self) -> JobStatusResponse:
        download_url = f"/api/jobs/{self.id}/download" if self.status == JobState.COMPLETED else None
        return JobStatusResponse(
            id=self.id,
            status=self.status.value,
            title=self.title,
            progress=self.progress,
            speed=self.speed,
            eta=self.eta,
            filename=self.filename,
            error=self.error,
            download_url=download_url
        )

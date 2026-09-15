import asyncio
import logging
from typing import Dict, Optional, List
from app.models import Job, JobState
from app.services.ytdlp_service import fetch_metadata, download_and_convert
from app.config import config
import shutil
import os

logger = logging.getLogger(__name__)

class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.active_workers: int = 0
        self.worker_task: Optional[asyncio.Task] = None

    def create_job(self, url: str) -> Job:
        job = Job(url=url)
        self.jobs[job.id] = job
        self.queue.put_nowait(job)
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    async def cancel_job(self, job_id: str) -> bool:
        job = self.get_job(job_id)
        if not job:
            return False
            
        if job.status in [JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED]:
            return False

        job.cancellation_requested = True
        job.status = JobState.CANCELLED
        
        if job.process:
            try:
                job.process.terminate()
            except ProcessLookupError:
                pass
                
        job.update()
        
        # Clean up files immediately
        job_dir = os.path.join(config.TEMP_DIR, job.id)
        if os.path.exists(job_dir):
            shutil.rmtree(job_dir, ignore_errors=True)
            
        return True

    def get_all_jobs(self) -> List[Job]:
        return list(self.jobs.values())

    def delete_job_record(self, job_id: str):
        if job_id in self.jobs:
            del self.jobs[job_id]

    async def worker(self):
        while True:
            job = await self.queue.get()
            
            if job.cancellation_requested:
                self.queue.task_done()
                continue
                
            self.active_workers += 1
            try:
                await self.process_job(job)
            except Exception as e:
                logger.error(f"Worker error processing job {job.id}: {e}")
                job.status = JobState.FAILED
                job.error = "Internal worker error"
                job.update()
            finally:
                self.active_workers -= 1
                self.queue.task_done()

    async def process_job(self, job: Job):
        job.status = JobState.FETCHING_METADATA
        job.update()
        
        metadata, error = await fetch_metadata(job.url)
        if job.cancellation_requested:
            return
            
        if error:
            job.status = JobState.FAILED
            job.error = error
            job.update()
            return
            
        job.title = metadata.get("title", f"Unknown Title {job.id}")
        job.update()
        
        await download_and_convert(job, config.TEMP_DIR)

    def start_workers(self):
        # We only start MAX_CONCURRENT_DOWNLOADS worker(s)
        for _ in range(config.MAX_CONCURRENT_DOWNLOADS):
            asyncio.create_task(self.worker())

job_manager = JobManager()

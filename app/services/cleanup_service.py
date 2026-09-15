import asyncio
import logging
import os
import shutil
from datetime import datetime
from app.services.job_manager import job_manager
from app.config import config
from app.models import JobState

logger = logging.getLogger(__name__)

async def cleanup_loop():
    """Background task to clean up old jobs and files."""
    while True:
        try:
            await asyncio.sleep(60)  # Check every minute
            
            now = datetime.utcnow()
            jobs_to_delete = []
            
            for job in job_manager.get_all_jobs():
                # We only clean up completed, failed, or cancelled jobs
                if job.status in [JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED]:
                    age = (now - job.updated_at).total_seconds()
                    
                    if age > config.CLEANUP_AGE_SECONDS:
                        logger.info(f"Cleaning up old job {job.id}")
                        
                        # Delete files
                        job_dir = os.path.join(config.TEMP_DIR, job.id)
                        if os.path.exists(job_dir):
                            shutil.rmtree(job_dir, ignore_errors=True)
                            
                        jobs_to_delete.append(job.id)
                        
            for jid in jobs_to_delete:
                job_manager.delete_job_record(jid)
                
            # Also clean up orphaned directories in TEMP_DIR
            if os.path.exists(config.TEMP_DIR):
                for item in os.listdir(config.TEMP_DIR):
                    item_path = os.path.join(config.TEMP_DIR, item)
                    if os.path.isdir(item_path):
                        # item is likely a job_id
                        if not job_manager.get_job(item):
                            # The job isn't in memory, maybe from a previous crash.
                            # We can safely delete it.
                            try:
                                stats = os.stat(item_path)
                                # Check if it's older than the cleanup age just to be safe
                                if (datetime.utcnow().timestamp() - stats.st_mtime) > config.CLEANUP_AGE_SECONDS:
                                    logger.info(f"Cleaning up orphaned directory {item_path}")
                                    shutil.rmtree(item_path, ignore_errors=True)
                            except Exception as e:
                                logger.error(f"Failed to cleanup orphaned dir {item_path}: {e}")
                                
        except Exception as e:
            logger.error(f"Error in cleanup loop: {e}")

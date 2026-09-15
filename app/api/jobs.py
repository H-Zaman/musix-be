from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from app.models import JobCreate, JobStatusResponse, JobState
from app.services.job_manager import job_manager
from app.utils.url import is_valid_youtube_url
import os

router = APIRouter()

@router.post("/jobs", status_code=status.HTTP_202_ACCEPTED, response_model=JobStatusResponse)
async def create_job(job_request: JobCreate):
    if not is_valid_youtube_url(job_request.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL.")
        
    job = job_manager.create_job(job_request.url)
    return job.to_response()

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job.to_response()

@router.delete("/jobs/{job_id}", response_model=JobStatusResponse)
async def cancel_job(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    success = await job_manager.cancel_job(job_id)
    
    if not success:
        # Job cannot be cancelled if completed/failed/cancelled
        return JSONResponse(
            status_code=409, 
            content={"detail": "Job cannot be cancelled in its current state.", "job": job.to_response().model_dump()}
        )
        
    return job.to_response()

@router.get("/jobs/{job_id}/download")
async def download_job(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    if job.status != JobState.COMPLETED or not job.output_path:
        raise HTTPException(status_code=409, detail="Job is not completed yet.")
        
    if not os.path.exists(job.output_path):
        raise HTTPException(status_code=404, detail="File not found on disk. It may have been cleaned up.")
        
    filename = job.filename or "audio.mp3"
    
    return FileResponse(
        path=job.output_path, 
        media_type="audio/mpeg", 
        filename=filename,
        content_disposition_type="attachment"
    )

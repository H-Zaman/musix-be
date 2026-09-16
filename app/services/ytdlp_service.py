import asyncio
import json
import logging
import os
from typing import Dict, Any, Tuple
from app.models import Job, JobState
from app.utils.filenames import sanitize_filename

logger = logging.getLogger(__name__)

async def fetch_metadata(url: str) -> Tuple[Dict[str, Any], str]:
    """Fetches metadata using yt-dlp without downloading."""
    process = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "--dump-json",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=default",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        error_msg = stderr.decode('utf-8').strip()
        logger.error(f"Failed to fetch metadata for {url}: {error_msg}")
        return {}, error_msg
        
    try:
        data = json.loads(stdout.decode('utf-8'))
        return data, ""
    except json.JSONDecodeError:
        return {}, "Failed to parse yt-dlp metadata JSON"

async def download_and_convert(job: Job, temp_dir: str):
    """Downloads and converts audio using yt-dlp, parsing progress."""
    job_dir = os.path.join(temp_dir, job.id)
    os.makedirs(job_dir, exist_ok=True)
    
    # We use a custom progress template to easily parse it
    # Format: %(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s
    progress_template = "%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s"
    
    # Output template: job_id.ext
    outtmpl = os.path.join(job_dir, f"{job.id}.%(ext)s")
    
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--no-playlist",
        "--extractor-args", "youtube:player_client=default",
        "--newline",
        "--progress-template", f"download:{progress_template}",
        "-o", outtmpl,
        job.url
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    job.process = process
    job.status = JobState.DOWNLOADING
    job.update()
    
    async def read_stream(stream, is_stderr: bool):
        while True:
            line = await stream.readline()
            if not line:
                break
            
            line_str = line.decode('utf-8', errors='ignore').strip()
            
            if job.cancellation_requested:
                break
                
            if is_stderr:
                logger.debug(f"[JOB {job.id}] stderr: {line_str}")
                continue
                
            # Parse progress template output
            if line_str.startswith("download:"):
                parts = line_str[9:].split('|')
                if len(parts) >= 3:
                    percent_str = parts[0].strip().replace('%', '')
                    speed_str = parts[1].strip()
                    eta_str = parts[2].strip()
                    
                    try:
                        # Sometimes yt-dlp outputs ANSI codes, so we strip them implicitly or handle errors
                        if percent_str and percent_str != 'NA':
                            job.progress = float(percent_str.replace('\x1b[0;94m', '').replace('\x1b[0m', ''))
                        if speed_str and speed_str != 'NA':
                            job.speed = speed_str
                        if eta_str and eta_str != 'NA':
                            job.eta = eta_str
                    except ValueError:
                        pass
                        
                    job.update()
                    
            elif "[ExtractAudio]" in line_str:
                job.status = JobState.CONVERTING
                job.progress = 100.0
                job.update()
                
    # Read both stdout and stderr concurrently
    await asyncio.gather(
        read_stream(process.stdout, False),
        read_stream(process.stderr, True)
    )
    
    await process.wait()
    job.process = None
    
    if job.cancellation_requested:
        job.status = JobState.CANCELLED
        job.update()
        return

    if process.returncode == 0:
        # Find the resulting mp3 file
        expected_mp3 = os.path.join(job_dir, f"{job.id}.mp3")
        if os.path.exists(expected_mp3):
            # Rename to sanitized title
            safe_title = sanitize_filename(job.title) if job.title else f"audio_{job.id}.mp3"
            if not safe_title.endswith(".mp3"):
                safe_title += ".mp3"
                
            final_path = os.path.join(job_dir, safe_title)
            
            # Avoid renaming to the same name or collision
            if expected_mp3 != final_path:
                os.rename(expected_mp3, final_path)
                
            job.output_path = final_path
            job.filename = safe_title
            job.status = JobState.COMPLETED
            job.progress = 100.0
            job.update()
        else:
            job.status = JobState.FAILED
            job.error = "File download completed but MP3 was not found."
            job.update()
    else:
        job.status = JobState.FAILED
        job.error = f"yt-dlp exited with code {process.returncode}"
        job.update()

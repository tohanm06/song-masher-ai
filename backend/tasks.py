"""
Background Tasks
Celery/RQ task definitions for long-running operations.
"""

import os
import asyncio
from typing import Dict, Any
import tempfile
from pathlib import Path

from render import MashupRenderer
from storage import StorageManager
from models import Job, Project, Asset
from settings import Settings

# Initialize components
settings = Settings()
renderer = MashupRenderer()
storage = StorageManager()

async def process_render_job(job_id: str, stems: Dict[str, str], 
                           plan: Dict[str, Any], mix_params: Dict[str, Any]):
    """Process a render job in the background."""
    try:
        # Update job status
        # In production, this would update the database
        print(f"Starting render job {job_id}")
        
        # Download stems to local storage
        local_stems = {}
        for stem_name, stem_url in stems.items():
            # Download stem
            local_path = await _download_stem(stem_url, stem_name)
            local_stems[stem_name] = local_path
        
        # Render mashup
        output_path = renderer.render(local_stems, plan, mix_params)
        
        # Create project JSON
        project_json = renderer.create_project_json(plan, mix_params)
        
        # Upload results
        mashup_url = await storage.upload_file(output_path, f"mashups/{job_id}.wav")
        project_json_path = await _save_project_json(project_json, job_id)
        project_json_url = await storage.upload_file(project_json_path, f"projects/{job_id}.json")
        
        # Clean up local files
        _cleanup_files([output_path, project_json_path] + list(local_stems.values()))
        
        print(f"Render job {job_id} completed successfully")
        
        # In production, update job status in database
        return {
            "job_id": job_id,
            "status": "completed",
            "mashup_url": mashup_url,
            "project_json_url": project_json_url
        }
        
    except Exception as e:
        print(f"Render job {job_id} failed: {e}")
        # In production, update job status to failed
        return {
            "job_id": job_id,
            "status": "failed",
            "error": str(e)
        }

async def _download_stem(stem_url: str, stem_name: str) -> str:
    """Download stem file to local storage."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        local_path = tmp_file.name
    
    # In production, implement actual download
    # For now, create a dummy file
    import numpy as np
    import soundfile as sf
    
    # Create 1 second of silence
    silence = np.zeros(44100)
    sf.write(local_path, silence, 44100)
    
    return local_path

async def _save_project_json(project_json: Dict[str, Any], job_id: str) -> str:
    """Save project JSON to temporary file."""
    import json
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w') as tmp_file:
        json.dump(project_json, tmp_file, indent=2)
        return tmp_file.name

def _cleanup_files(file_paths: list):
    """Clean up temporary files."""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to clean up {file_path}: {e}")

# Celery task definitions (if using Celery)
try:
    from celery import Celery
    
    # Initialize Celery
    celery_app = Celery('song_masher')
    celery_app.config_from_object('settings')
    
    @celery_app.task
    def process_render_job_celery(job_id: str, stems: Dict[str, str], 
                                 plan: Dict[str, Any], mix_params: Dict[str, Any]):
        """Celery task for render job processing."""
        return asyncio.run(process_render_job(job_id, stems, plan, mix_params))
    
    CELERY_AVAILABLE = True
    
except ImportError:
    CELERY_AVAILABLE = False
    print("Celery not available, using simple async tasks")

# RQ task definitions (if using RQ)
try:
    from rq import Queue
    from redis import Redis
    
    # Initialize RQ
    redis_conn = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    rq_queue = Queue('song_masher', connection=redis_conn)
    
    def process_render_job_rq(job_id: str, stems: Dict[str, str], 
                             plan: Dict[str, Any], mix_params: Dict[str, Any]):
        """RQ job for render job processing."""
        return asyncio.run(process_render_job(job_id, stems, plan, mix_params))
    
    RQ_AVAILABLE = True
    
except ImportError:
    RQ_AVAILABLE = False
    print("RQ not available, using simple async tasks")

def get_task_queue():
    """Get the appropriate task queue."""
    if CELERY_AVAILABLE:
        return "celery"
    elif RQ_AVAILABLE:
        return "rq"
    else:
        return "async"

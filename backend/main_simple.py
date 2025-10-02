"""
Song Masher AI - FastAPI Backend (Simplified)
Production-grade audio mashup API with stem separation, analysis, and rendering.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
import shutil

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

from analysis_simple import AudioAnalyzer
from separation import StemSeparator
from planning import MashupPlanner
from render import MashupRenderer
from models import Project, Job, Asset
from storage import StorageManager
from tasks import process_render_job
from settings import Settings

# Initialize FastAPI app
app = FastAPI(
    title="Song Masher AI",
    description="Production-grade audio mashup API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
settings = Settings()
analyzer = AudioAnalyzer()
separator = StemSeparator()
planner = MashupPlanner()
renderer = MashupRenderer()
storage = StorageManager()

# Pydantic models
class AnalysisRequest(BaseModel):
    pass

class AnalysisResponse(BaseModel):
    duration: float
    bpm: float
    beats: List[float]
    downbeats: List[float]
    key: str
    camelot: str
    sections: List[Dict[str, Any]]
    lufs: float

class SeparationResponse(BaseModel):
    vocals: str
    drums: str
    bass: str
    other: str

class PlanRequest(BaseModel):
    trackA: Dict[str, Any]
    trackB: Dict[str, Any]
    recipe: str  # "AoverB", "BoverA", "HybridDrums"

class PlanResponse(BaseModel):
    targetKey: str
    keyShiftA: int
    keyShiftB: int
    stretchMap: Dict[str, float]
    sectionPairs: List[Dict[str, Any]]
    qualityHints: List[str]

class RenderRequest(BaseModel):
    stems: Dict[str, str]
    plan: Dict[str, Any]
    mixParams: Dict[str, Any]

class RenderResponse(BaseModel):
    jobId: str

@app.get("/health")
async def health_check():
    """Health check endpoint with version info."""
    try:
        import torch
        import demucs
        
        return {
            "status": "ok",
            "versions": {
                "torch": torch.__version__,
                "demucs": demucs.__version__,
                "librosa": "0.11.0"
            }
        }
    except ImportError as e:
        return {
            "status": "error",
            "error": f"Missing dependency: {e}"
        }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...)):
    """Analyze uploaded audio for BPM, key, structure, and loudness."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file.flush()
        
        try:
            # Analyze audio
            result = analyzer.analyze(tmp_file.name)
            
            return AnalysisResponse(
                duration=result["duration"],
                bpm=result["bpm"],
                beats=result["beats"],
                downbeats=result["downbeats"],
                key=result["key"],
                camelot=result["camelot"],
                sections=result["sections"],
                lufs=result["lufs"]
            )
        finally:
            # Clean up temp file
            os.unlink(tmp_file.name)

@app.post("/separate", response_model=SeparationResponse)
async def separate_stems(file: UploadFile = File(...)):
    """Extract stems from uploaded audio."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file.flush()
        
        try:
            # Separate stems
            stems = separator.separate(tmp_file.name)
            
            # Upload stems to storage and get URLs
            stem_urls = {}
            for stem_name, stem_path in stems.items():
                url = await storage.upload_file(stem_path, f"stems/{stem_name}")
                stem_urls[stem_name] = url
                
                # Clean up local stem file
                os.unlink(stem_path)
            
            return SeparationResponse(**stem_urls)
        finally:
            # Clean up temp file
            os.unlink(tmp_file.name)

@app.post("/plan", response_model=PlanResponse)
async def plan_mashup(request: PlanRequest):
    """Generate mashup strategy with key/tempo alignment."""
    try:
        plan = planner.create_plan(
            trackA=request.trackA,
            trackB=request.trackB,
            recipe=request.recipe
        )
        
        return PlanResponse(
            targetKey=plan["targetKey"],
            keyShiftA=plan["keyShiftA"],
            keyShiftB=plan["keyShiftB"],
            stretchMap=plan["stretchMap"],
            sectionPairs=plan["sectionPairs"],
            qualityHints=plan["qualityHints"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Planning failed: {str(e)}")

@app.post("/render", response_model=RenderResponse)
async def render_mashup(request: RenderRequest, background_tasks: BackgroundTasks):
    """Queue mashup render job."""
    try:
        # Create job record
        job = Job(
            status="queued",
            stems=request.stems,
            plan=request.plan,
            mixParams=request.mixParams
        )
        job_id = str(job.id)
        
        # Queue background task
        background_tasks.add_task(
            process_render_job,
            job_id,
            request.stems,
            request.plan,
            request.mixParams
        )
        
        return RenderResponse(jobId=job_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Render queue failed: {str(e)}")

@app.get("/progress/{job_id}")
async def get_progress(job_id: str):
    """Get render job progress."""
    # In a real implementation, this would query the database
    # For now, return a simple status
    return {
        "jobId": job_id,
        "status": "processing",
        "progress": 0.5,
        "message": "Rendering mashup..."
    }

@app.get("/download/{job_id}")
async def download_mashup(job_id: str):
    """Download completed mashup and project.json."""
    # In a real implementation, this would:
    # 1. Check job status
    # 2. Get file URLs from storage
    # 3. Return signed URLs or stream files
    
    # For now, return placeholder
    return {
        "mashup_url": f"https://storage.example.com/mashups/{job_id}.wav",
        "project_url": f"https://storage.example.com/projects/{job_id}.json"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

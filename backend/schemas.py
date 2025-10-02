"""
Pydantic Schemas
Request/response models for API validation.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    """Request model for audio analysis."""
    pass

class AnalysisResponse(BaseModel):
    """Response model for audio analysis."""
    duration: float = Field(..., description="Audio duration in seconds")
    bpm: float = Field(..., description="Beats per minute")
    beats: List[float] = Field(..., description="Beat timestamps")
    downbeats: List[float] = Field(..., description="Downbeat timestamps")
    key: str = Field(..., description="Musical key (e.g., 'Cm', 'F#m')")
    camelot: str = Field(..., description="Camelot wheel notation (e.g., '5A', '8B')")
    sections: List[Dict[str, Any]] = Field(..., description="Section analysis")
    lufs: float = Field(..., description="Integrated loudness in LUFS")

class SeparationRequest(BaseModel):
    """Request model for stem separation."""
    pass

class SeparationResponse(BaseModel):
    """Response model for stem separation."""
    vocals: str = Field(..., description="URL to vocals stem")
    drums: str = Field(..., description="URL to drums stem")
    bass: str = Field(..., description="URL to bass stem")
    other: str = Field(..., description="URL to other instruments stem")

class PlanRequest(BaseModel):
    """Request model for mashup planning."""
    trackA: Dict[str, Any] = Field(..., description="Analysis data for track A")
    trackB: Dict[str, Any] = Field(..., description="Analysis data for track B")
    recipe: str = Field(..., description="Mashup recipe: AoverB, BoverA, HybridDrums")

class PlanResponse(BaseModel):
    """Response model for mashup planning."""
    targetKey: str = Field(..., description="Target key for mashup")
    keyShiftA: int = Field(..., description="Key shift for track A in semitones")
    keyShiftB: int = Field(..., description="Key shift for track B in semitones")
    stretchMap: Dict[str, float] = Field(..., description="Tempo stretch ratios")
    sectionPairs: List[Dict[str, Any]] = Field(..., description="Aligned section pairs")
    qualityHints: List[str] = Field(..., description="Quality assessment hints")

class RenderRequest(BaseModel):
    """Request model for mashup rendering."""
    stems: Dict[str, str] = Field(..., description="Stem file URLs")
    plan: Dict[str, Any] = Field(..., description="Mashup plan")
    mixParams: Dict[str, Any] = Field(..., description="Mixing parameters")

class RenderResponse(BaseModel):
    """Response model for mashup rendering."""
    jobId: str = Field(..., description="Render job ID")

class ProgressResponse(BaseModel):
    """Response model for job progress."""
    jobId: str = Field(..., description="Job ID")
    status: str = Field(..., description="Job status")
    progress: float = Field(..., description="Progress percentage (0-1)")
    message: str = Field(..., description="Status message")

class DownloadResponse(BaseModel):
    """Response model for download links."""
    mashup_url: str = Field(..., description="URL to final mashup")
    project_url: str = Field(..., description="URL to project.json")

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    versions: Dict[str, str] = Field(..., description="Component versions")

class ProjectCreate(BaseModel):
    """Request model for project creation."""
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    recipe: str = Field(..., description="Mashup recipe")

class ProjectResponse(BaseModel):
    """Response model for project data."""
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    recipe: str = Field(..., description="Mashup recipe")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class JobResponse(BaseModel):
    """Response model for job data."""
    id: str = Field(..., description="Job ID")
    project_id: str = Field(..., description="Project ID")
    status: str = Field(..., description="Job status")
    progress: float = Field(..., description="Progress percentage")
    message: Optional[str] = Field(None, description="Status message")
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

class AssetResponse(BaseModel):
    """Response model for asset data."""
    id: str = Field(..., description="Asset ID")
    asset_type: str = Field(..., description="Asset type")
    file_path: str = Field(..., description="File path")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    bpm: Optional[float] = Field(None, description="BPM")
    key: Optional[str] = Field(None, description="Musical key")
    camelot: Optional[str] = Field(None, description="Camelot notation")
    lufs: Optional[float] = Field(None, description="LUFS loudness")
    created_at: datetime = Field(..., description="Creation timestamp")

class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    code: Optional[str] = Field(None, description="Error code")

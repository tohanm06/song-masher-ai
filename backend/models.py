"""
Database Models
SQLAlchemy models for project, job, and asset management.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Project(Base):
    """Project model for mashup projects."""
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Project settings
    recipe = Column(String, nullable=False)  # "AoverB", "BoverA", "HybridDrums"
    target_key = Column(String)
    target_bpm = Column(Float)
    
    # Relationships
    jobs = relationship("Job", back_populates="project")
    assets = relationship("Asset", back_populates="project")

class Job(Base):
    """Job model for render jobs."""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"))
    status = Column(String, nullable=False, default="queued")  # queued, processing, completed, failed
    progress = Column(Float, default=0.0)
    message = Column(Text)
    
    # Job parameters
    stems = Column(Text)  # JSON string of stem URLs
    plan = Column(Text)   # JSON string of mashup plan
    mix_params = Column(Text)  # JSON string of mixing parameters
    
    # Results
    output_url = Column(String)  # URL to final mashup
    project_json_url = Column(String)  # URL to project.json
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    project = relationship("Project", back_populates="jobs")

class Asset(Base):
    """Asset model for uploaded files and generated content."""
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"))
    asset_type = Column(String, nullable=False)  # "upload", "stem", "mashup", "project_json"
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    
    # Analysis data
    duration = Column(Float)
    bpm = Column(Float)
    key = Column(String)
    camelot = Column(String)
    lufs = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="assets")

class User(Base):
    """User model for authentication (optional)."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    projects = relationship("Project", back_populates="user")

# Add user relationship to Project
Project.user_id = Column(String, ForeignKey("users.id"))
Project.user = relationship("User", back_populates="projects")

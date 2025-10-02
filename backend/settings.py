"""
Settings and Configuration
Environment-based configuration management.
"""

import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Core settings
    simple_mode: bool = False
    allow_audio_storage: bool = False
    
    # Storage settings
    storage_kind: str = "local"  # s3, minio, local
    
    # Database settings
    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/postgres"
    
    # Redis settings
    redis_url: str = "redis://redis:6379/0"
    
    # AWS S3 settings
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: Optional[str] = None
    aws_s3_region: str = "us-east-1"
    
    # MinIO settings
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "song-masher"
    
    # Local storage settings
    local_storage_path: str = "./storage"
    
    # Audio processing settings
    sample_rate: int = 44100
    target_lufs: float = -14.0
    headroom_db: float = 1.0
    
    # Model settings
    demucs_model: str = "htdemucs"
    demucs_device: Optional[str] = None
    
    # Celery settings (if using Celery)
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"
    
    # CORS settings
    cors_origins: list = ["http://localhost:3000", "http://frontend:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting."""
        return self.database_url
    
    def get_redis_url(self) -> str:
        """Get Redis URL with proper formatting."""
        return self.redis_url
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration."""
        if self.storage_kind == "s3":
            return {
                "kind": "s3",
                "access_key": self.aws_access_key_id,
                "secret_key": self.aws_secret_access_key,
                "bucket": self.aws_s3_bucket,
                "region": self.aws_s3_region
            }
        elif self.storage_kind == "minio":
            return {
                "kind": "minio",
                "endpoint": self.minio_endpoint,
                "access_key": self.minio_access_key,
                "secret_key": self.minio_secret_key,
                "bucket": self.minio_bucket
            }
        else:  # local
            return {
                "kind": "local",
                "path": self.local_storage_path
            }
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return {
            "demucs_model": self.demucs_model,
            "demucs_device": self.demucs_device or ("cuda" if self._cuda_available() else "cpu"),
            "sample_rate": self.sample_rate
        }
    
    def _cuda_available(self) -> bool:
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio processing configuration."""
        return {
            "sample_rate": self.sample_rate,
            "target_lufs": self.target_lufs,
            "headroom_db": self.headroom_db
        }
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return os.getenv("ENVIRONMENT", "development") == "production"
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return os.getenv("ENVIRONMENT", "development") == "development"
    
    def get_cors_origins(self) -> list:
        """Get CORS origins."""
        if self.is_production():
            return ["https://yourdomain.com"]  # Update for production
        else:
            return self.cors_origins

# Global settings instance
settings = Settings()

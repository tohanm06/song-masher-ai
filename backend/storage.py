"""
Storage Management
S3/MinIO storage abstraction for audio files and metadata.
"""

import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
import tempfile
from pathlib import Path

class StorageManager:
    """Unified storage interface for S3, MinIO, and local storage."""
    
    def __init__(self, storage_kind: str = "local"):
        self.storage_kind = storage_kind
        self.client = None
        self.bucket_name = None
        
        if storage_kind in ["s3", "minio"]:
            self._init_s3_client()
        elif storage_kind == "local":
            self._init_local_storage()
    
    def _init_s3_client(self):
        """Initialize S3/MinIO client."""
        try:
            if self.storage_kind == "s3":
                self.client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_S3_REGION', 'us-east-1')
                )
                self.bucket_name = os.getenv('AWS_S3_BUCKET')
            else:  # MinIO
                self.client = boto3.client(
                    's3',
                    endpoint_url=f"http://{os.getenv('MINIO_ENDPOINT', 'minio:9000')}",
                    aws_access_key_id=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
                    aws_secret_access_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
                    region_name='us-east-1'
                )
                self.bucket_name = os.getenv('MINIO_BUCKET', 'song-masher')
            
            # Ensure bucket exists
            self._ensure_bucket_exists()
            
        except Exception as e:
            print(f"Failed to initialize S3 client: {e}")
            self.client = None
    
    def _init_local_storage(self):
        """Initialize local storage."""
        self.local_storage_path = Path(os.getenv('LOCAL_STORAGE_PATH', './storage'))
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
    
    def _ensure_bucket_exists(self):
        """Ensure S3 bucket exists."""
        if not self.client or not self.bucket_name:
            return
        
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket doesn't exist, create it
                try:
                    if self.storage_kind == "s3":
                        self.client.create_bucket(Bucket=self.bucket_name)
                    else:  # MinIO
                        self.client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': 'us-east-1'}
                        )
                except Exception as create_error:
                    print(f"Failed to create bucket: {create_error}")
    
    async def upload_file(self, file_path: str, key: str) -> str:
        """Upload file to storage and return URL."""
        if self.storage_kind == "local":
            return self._upload_local(file_path, key)
        elif self.client:
            return self._upload_s3(file_path, key)
        else:
            raise RuntimeError("Storage not properly initialized")
    
    def _upload_local(self, file_path: str, key: str) -> str:
        """Upload file to local storage."""
        source_path = Path(file_path)
        dest_path = self.local_storage_path / key
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        import shutil
        shutil.copy2(source_path, dest_path)
        
        # Return local URL
        return f"file://{dest_path.absolute()}"
    
    def _upload_s3(self, file_path: str, key: str) -> str:
        """Upload file to S3/MinIO."""
        try:
            self.client.upload_file(file_path, self.bucket_name, key)
            
            # Generate URL
            if self.storage_kind == "s3":
                region = os.getenv('AWS_S3_REGION', 'us-east-1')
                url = f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{key}"
            else:  # MinIO
                endpoint = os.getenv('MINIO_ENDPOINT', 'minio:9000')
                url = f"http://{endpoint}/{self.bucket_name}/{key}"
            
            return url
            
        except Exception as e:
            raise RuntimeError(f"Upload failed: {e}")
    
    async def download_file(self, key: str, local_path: str) -> str:
        """Download file from storage."""
        if self.storage_kind == "local":
            return self._download_local(key, local_path)
        elif self.client:
            return self._download_s3(key, local_path)
        else:
            raise RuntimeError("Storage not properly initialized")
    
    def _download_local(self, key: str, local_path: str) -> str:
        """Download file from local storage."""
        source_path = self.local_storage_path / key
        dest_path = Path(local_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(source_path, dest_path)
        return str(dest_path)
    
    def _download_s3(self, key: str, local_path: str) -> str:
        """Download file from S3/MinIO."""
        try:
            self.client.download_file(self.bucket_name, key, local_path)
            return local_path
        except Exception as e:
            raise RuntimeError(f"Download failed: {e}")
    
    async def delete_file(self, key: str) -> bool:
        """Delete file from storage."""
        if self.storage_kind == "local":
            return self._delete_local(key)
        elif self.client:
            return self._delete_s3(key)
        else:
            return False
    
    def _delete_local(self, key: str) -> bool:
        """Delete file from local storage."""
        try:
            file_path = self.local_storage_path / key
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def _delete_s3(self, key: str) -> bool:
        """Delete file from S3/MinIO."""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False
    
    async def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for file access."""
        if self.storage_kind == "local":
            # For local storage, return file URL
            file_path = self.local_storage_path / key
            return f"file://{file_path.absolute()}"
        elif self.client:
            try:
                url = self.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': key},
                    ExpiresIn=expiration
                )
                return url
            except Exception as e:
                raise RuntimeError(f"Presigned URL generation failed: {e}")
        else:
            raise RuntimeError("Storage not properly initialized")
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage configuration info."""
        return {
            "storage_kind": self.storage_kind,
            "bucket_name": self.bucket_name,
            "local_path": str(self.local_storage_path) if self.storage_kind == "local" else None,
            "client_available": self.client is not None
        }

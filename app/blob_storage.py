"""
Azure Blob Storage service for managing file uploads and storage.
"""

from typing import Optional, BinaryIO
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.identity import DefaultAzureCredential
import logging

from .config import AzureConfig

logger = logging.getLogger(__name__)


class BlobStorageService:
    """Service for managing Azure Blob Storage operations."""
    
    def __init__(self, config: AzureConfig):
        """Initialize the blob storage service."""
        self.config = config
        self.blob_service_client = self._create_blob_service_client()
    
    def _create_blob_service_client(self) -> BlobServiceClient:
        """Create and return a BlobServiceClient."""
        if self.config.use_managed_identity:
            credential = DefaultAzureCredential()
            account_url = f"https://{self.config.storage_account_name}.blob.core.windows.net"
            return BlobServiceClient(account_url=account_url, credential=credential)
        else:
            return BlobServiceClient.from_connection_string(
                self.config.storage_connection_string
            )
    
    def create_container(self, container_name: str) -> ContainerClient:
        """Create a new container if it doesn't exist."""
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            
            if not container_client.exists():
                container_client = self.blob_service_client.create_container(container_name)
                logger.info(f"Created container: {container_name}")
            else:
                logger.info(f"Container already exists: {container_name}")
            
            return container_client
        except Exception as e:
            logger.error(f"Error creating container {container_name}: {e}")
            raise
    
    def upload_file(
        self,
        container_name: str,
        blob_name: str,
        data: BinaryIO,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> str:
        """Upload a file to blob storage."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            # Upload the blob
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings={'content_type': content_type} if content_type else None,
                metadata=metadata
            )
            
            logger.info(f"Uploaded blob: {blob_name} to container: {container_name}")
            return blob_client.url
        except Exception as e:
            logger.error(f"Error uploading blob {blob_name}: {e}")
            raise
    
    def download_file(self, container_name: str, blob_name: str) -> bytes:
        """Download a file from blob storage."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            return blob_client.download_blob().readall()
        except Exception as e:
            logger.error(f"Error downloading blob {blob_name}: {e}")
            raise
    
    def delete_file(self, container_name: str, blob_name: str) -> None:
        """Delete a file from blob storage."""
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            blob_client.delete_blob()
            logger.info(f"Deleted blob: {blob_name} from container: {container_name}")
        except Exception as e:
            logger.error(f"Error deleting blob {blob_name}: {e}")
            raise
    
    def list_files(self, container_name: str, prefix: Optional[str] = None):
        """List files in a container."""
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            return container_client.list_blobs(name_starts_with=prefix)
        except Exception as e:
            logger.error(f"Error listing blobs in container {container_name}: {e}")
            raise

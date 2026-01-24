"""
Blob storage service for storing audio files.
Supports both mock mode (local filesystem) and Azure Blob Storage.
"""

import logging
import uuid
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

# Azure Blob Storage import (optional, only needed when MOCK_MODE=false)
try:
    from azure.storage.blob import BlobServiceClient, ContentSettings

    AZURE_BLOB_AVAILABLE = True
except ImportError:
    AZURE_BLOB_AVAILABLE = False
    logger.warning("Azure Blob Storage SDK not available. Only mock mode will work.")


class BlobStorageService:
    """
    Service for storing audio files in blob storage.

    In mock mode: Saves to local filesystem (./mock_blob_storage/).
    In Azure mode: Uploads to Azure Blob Storage.
    """

    def __init__(self):
        self.mock_mode = settings.MOCK_MODE

        if not self.mock_mode:
            if not AZURE_BLOB_AVAILABLE:
                raise RuntimeError(
                    "Azure Blob Storage SDK is not available. "
                    "Install with: pip install azure-storage-blob"
                )

            self.blob_service_client = BlobServiceClient.from_connection_string(
                settings.BLOB_CONNECTION_STRING
            )
            self.container_name = settings.BLOB_CONTAINER_NAME

            # Ensure container exists
            self._ensure_container_exists()

    def _ensure_container_exists(self):
        """Create container if it doesn't exist (Azure mode only)."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"Created blob container: {self.container_name}")
        except Exception as e:
            logger.error(f"Failed to ensure container exists: {str(e)}")
            raise

    async def upload_audio(
        self, audio_bytes: bytes, file_extension: str = "wav", user_id: str | None = None
    ) -> str:
        """
        Upload audio file to storage.

        Args:
            audio_bytes: Audio file content (should already be encrypted)
            file_extension: File extension (default: wav)
            user_id: Optional user ID for organizing files

        Returns:
            URL or path to the stored file

        Raises:
            Exception: If upload fails
        """
        if self.mock_mode:
            return self._mock_upload(audio_bytes, file_extension, user_id)

        return await self._azure_upload(audio_bytes, file_extension, user_id)

    def _mock_upload(self, audio_bytes: bytes, file_extension: str, user_id: str | None) -> str:
        """
        Save audio to local filesystem for development.

        Organizes files by user_id if provided.
        """
        try:
            # Create unique filename
            filename = f"{uuid.uuid4()}.{file_extension}"

            # Organize by user if provided
            if user_id:
                local_path = Path("./mock_blob_storage") / user_id / filename
            else:
                local_path = Path("./mock_blob_storage") / filename

            # Ensure directory exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(local_path, "wb") as f:
                f.write(audio_bytes)

            logger.info(f"Mock upload: Saved {len(audio_bytes)} bytes to {local_path}")

            # Return mock URL
            return f"local://{local_path.relative_to('.')}"

        except Exception as e:
            logger.error(f"Mock upload failed: {str(e)}")
            raise Exception(f"File upload failed: {str(e)}")

    async def _azure_upload(
        self, audio_bytes: bytes, file_extension: str, user_id: str | None
    ) -> str:
        """
        Upload audio to Azure Blob Storage.

        Organizes blobs by user_id and timestamp for easy management.
        """
        try:
            # Create unique blob name
            from datetime import datetime

            timestamp = datetime.utcnow().strftime("%Y%m%d")

            if user_id:
                blob_name = f"assessments/{user_id}/{timestamp}/{uuid.uuid4()}.{file_extension}"
            else:
                blob_name = f"assessments/anonymous/{timestamp}/{uuid.uuid4()}.{file_extension}"

            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            # Upload with appropriate content type
            content_settings = ContentSettings(content_type="audio/wav")

            blob_client.upload_blob(audio_bytes, overwrite=True, content_settings=content_settings)

            # Return blob URL
            blob_url = blob_client.url

            logger.info(f"Azure upload: Uploaded {len(audio_bytes)} bytes to {blob_name}")

            return blob_url

        except Exception as e:
            logger.error(f"Azure upload failed: {str(e)}")
            raise Exception(f"File upload failed: {str(e)}")

    async def download_audio(self, blob_url: str) -> bytes:
        """
        Download audio file from storage.

        Args:
            blob_url: URL or path to the stored file

        Returns:
            Audio file bytes (encrypted)

        Raises:
            Exception: If download fails
        """
        if blob_url.startswith("local://"):
            return self._mock_download(blob_url)

        return await self._azure_download(blob_url)

    def _mock_download(self, blob_url: str) -> bytes:
        """Download from local filesystem."""
        try:
            # Extract path from mock URL
            local_path = Path(blob_url.replace("local://", ""))

            with open(local_path, "rb") as f:
                audio_bytes = f.read()

            logger.info(f"Mock download: Read {len(audio_bytes)} bytes from {local_path}")
            return audio_bytes

        except Exception as e:
            logger.error(f"Mock download failed: {str(e)}")
            raise Exception(f"File download failed: {str(e)}")

    async def _azure_download(self, blob_url: str) -> bytes:
        """Download from Azure Blob Storage."""
        try:
            # Extract blob name from URL
            blob_name = blob_url.split(f"{self.container_name}/")[-1]

            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            # Download blob
            audio_bytes = blob_client.download_blob().readall()

            logger.info(f"Azure download: Downloaded {len(audio_bytes)} bytes from {blob_name}")
            return audio_bytes

        except Exception as e:
            logger.error(f"Azure download failed: {str(e)}")
            raise Exception(f"File download failed: {str(e)}")

    async def delete_audio(self, blob_url: str) -> bool:
        """
        Delete audio file from storage.

        Args:
            blob_url: URL or path to the stored file

        Returns:
            True if deletion was successful

        Raises:
            Exception: If deletion fails
        """
        if blob_url.startswith("local://"):
            return self._mock_delete(blob_url)

        return await self._azure_delete(blob_url)

    def _mock_delete(self, blob_url: str) -> bool:
        """Delete from local filesystem."""
        try:
            local_path = Path(blob_url.replace("local://", ""))

            if local_path.exists():
                local_path.unlink()
                logger.info(f"Mock delete: Removed {local_path}")
                return True
            else:
                logger.warning(f"Mock delete: File not found {local_path}")
                return False

        except Exception as e:
            logger.error(f"Mock delete failed: {str(e)}")
            raise Exception(f"File deletion failed: {str(e)}")

    async def _azure_delete(self, blob_url: str) -> bool:
        """Delete from Azure Blob Storage."""
        try:
            blob_name = blob_url.split(f"{self.container_name}/")[-1]

            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            blob_client.delete_blob()
            logger.info(f"Azure delete: Removed {blob_name}")
            return True

        except Exception as e:
            logger.error(f"Azure delete failed: {str(e)}")
            raise Exception(f"File deletion failed: {str(e)}")

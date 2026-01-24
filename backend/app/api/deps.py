"""
API dependencies for dependency injection.
Provides database sessions and service instances to endpoints.
"""

from app.db.session import get_db
from app.services.blob_service import BlobStorageService
from app.services.encryption_service import EncryptionService
from app.services.speech_service import SpeechAssessmentService

# Re-export get_db for convenience
__all__ = ["get_db", "get_speech_service", "get_blob_service", "get_encryption_service"]


def get_speech_service() -> SpeechAssessmentService:
    """Dependency to get speech assessment service instance."""
    return SpeechAssessmentService()


def get_blob_service() -> BlobStorageService:
    """Dependency to get blob storage service instance."""
    return BlobStorageService()


def get_encryption_service() -> EncryptionService:
    """Dependency to get encryption service instance."""
    return EncryptionService()

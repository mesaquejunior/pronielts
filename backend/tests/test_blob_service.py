"""Unit tests for the blob storage service (mock mode)."""

import pytest
from pathlib import Path
import shutil

from app.services.blob_service import BlobStorageService


@pytest.fixture(autouse=True)
def cleanup_mock_storage():
    """Clean up mock blob storage after each test."""
    yield
    mock_dir = Path("./mock_blob_storage")
    if mock_dir.exists():
        shutil.rmtree(mock_dir)


class TestBlobServiceMockUpload:
    """Test suite for mock upload functionality."""

    @pytest.mark.asyncio
    async def test_upload_audio(self):
        service = BlobStorageService()
        audio_bytes = b"fake audio bytes"
        url = await service.upload_audio(audio_bytes)
        assert url.startswith("local://")
        assert url.endswith(".wav")

    @pytest.mark.asyncio
    async def test_upload_audio_custom_extension(self):
        service = BlobStorageService()
        url = await service.upload_audio(b"data", file_extension="mp3")
        assert url.endswith(".mp3")

    @pytest.mark.asyncio
    async def test_upload_audio_with_user_id(self):
        service = BlobStorageService()
        url = await service.upload_audio(b"data", user_id="user-123")
        assert "user-123" in url

    @pytest.mark.asyncio
    async def test_upload_creates_file(self):
        service = BlobStorageService()
        audio_bytes = b"test file content"
        url = await service.upload_audio(audio_bytes)

        # Extract path and verify file exists
        file_path = Path(url.replace("local://", ""))
        assert file_path.exists()
        assert file_path.read_bytes() == audio_bytes


class TestBlobServiceMockDownload:
    """Test suite for mock download functionality."""

    @pytest.mark.asyncio
    async def test_download_audio(self):
        service = BlobStorageService()
        original = b"audio data to download"
        url = await service.upload_audio(original)

        downloaded = await service.download_audio(url)
        assert downloaded == original

    @pytest.mark.asyncio
    async def test_download_nonexistent_file(self):
        service = BlobStorageService()
        with pytest.raises(Exception, match="File download failed"):
            await service.download_audio("local://nonexistent/file.wav")


class TestBlobServiceMockDelete:
    """Test suite for mock delete functionality."""

    @pytest.mark.asyncio
    async def test_delete_audio(self):
        service = BlobStorageService()
        url = await service.upload_audio(b"to be deleted")

        result = await service.delete_audio(url)
        assert result is True

        # Verify file is gone
        file_path = Path(url.replace("local://", ""))
        assert not file_path.exists()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_file(self):
        service = BlobStorageService()
        result = await service.delete_audio("local://nonexistent.wav")
        assert result is False

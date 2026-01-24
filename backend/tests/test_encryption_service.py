"""Unit tests for the encryption service."""

import pytest
from cryptography.fernet import Fernet, InvalidToken

from app.services.encryption_service import EncryptionService


class TestEncryptionService:
    """Test suite for EncryptionService."""

    def test_encrypt_audio(self):
        service = EncryptionService()
        audio_bytes = b"fake audio content for testing"
        encrypted = service.encrypt_audio(audio_bytes)
        assert encrypted != audio_bytes
        assert len(encrypted) > len(audio_bytes)

    def test_decrypt_audio(self):
        service = EncryptionService()
        audio_bytes = b"fake audio content for testing"
        encrypted = service.encrypt_audio(audio_bytes)
        decrypted = service.decrypt_audio(encrypted)
        assert decrypted == audio_bytes

    def test_encrypt_decrypt_roundtrip(self):
        service = EncryptionService()
        original = b"\x00\x01\x02" * 1000  # binary data
        encrypted = service.encrypt_audio(original)
        decrypted = service.decrypt_audio(encrypted)
        assert decrypted == original

    def test_decrypt_invalid_token(self):
        service = EncryptionService()
        with pytest.raises(InvalidToken):
            service.decrypt_audio(b"not-valid-encrypted-data")

    def test_decrypt_wrong_key(self):
        service = EncryptionService()
        # Encrypt with a different key
        other_key = Fernet.generate_key()
        other_cipher = Fernet(other_key)
        encrypted = other_cipher.encrypt(b"secret audio")

        with pytest.raises(InvalidToken):
            service.decrypt_audio(encrypted)

    def test_rotate_key(self):
        old_key = Fernet.generate_key().decode()
        new_key = Fernet.generate_key().decode()

        # Encrypt with old key
        old_cipher = Fernet(old_key.encode())
        original_data = b"audio data to rotate"
        encrypted_with_old = old_cipher.encrypt(original_data)

        # Rotate
        service = EncryptionService()
        re_encrypted = service.rotate_key(old_key, new_key, encrypted_with_old)

        # Verify new key can decrypt
        new_cipher = Fernet(new_key.encode())
        decrypted = new_cipher.decrypt(re_encrypted)
        assert decrypted == original_data

    def test_encrypt_empty_bytes(self):
        service = EncryptionService()
        encrypted = service.encrypt_audio(b"")
        decrypted = service.decrypt_audio(encrypted)
        assert decrypted == b""

    def test_encrypt_large_data(self):
        service = EncryptionService()
        large_data = b"\x00" * (1024 * 1024)  # 1MB
        encrypted = service.encrypt_audio(large_data)
        decrypted = service.decrypt_audio(encrypted)
        assert decrypted == large_data

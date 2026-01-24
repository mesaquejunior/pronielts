"""
Encryption service for securing audio files before storage.
Uses Fernet (symmetric encryption) with AES-256.
"""

import logging

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    Service for encrypting and decrypting audio files.

    Uses Fernet (symmetric encryption) which provides:
    - AES-256 encryption
    - HMAC for authentication
    - Timestamp for expiration (if needed)
    """

    def __init__(self):
        """Initialize encryption service with key from settings."""
        try:
            self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        except Exception as e:
            raise ValueError(
                "Invalid ENCRYPTION_KEY in settings. "
                "Generate a valid key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            ) from e

    def encrypt_audio(self, audio_bytes: bytes) -> bytes:
        """
        Encrypt audio file bytes.

        Args:
            audio_bytes: Raw audio file content

        Returns:
            Encrypted bytes

        Raises:
            Exception: If encryption fails
        """
        try:
            encrypted = self.cipher.encrypt(audio_bytes)
            logger.info(f"Encrypted audio: {len(audio_bytes)} bytes -> {len(encrypted)} bytes")
            return encrypted
        except Exception as e:
            logger.error(f"Audio encryption failed: {str(e)}")
            raise Exception(f"Encryption failed: {str(e)}")

    def decrypt_audio(self, encrypted_bytes: bytes) -> bytes:
        """
        Decrypt audio file bytes.

        Args:
            encrypted_bytes: Encrypted audio content

        Returns:
            Decrypted bytes

        Raises:
            InvalidToken: If decryption fails (wrong key or corrupted data)
            Exception: For other decryption errors
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_bytes)
            logger.info(f"Decrypted audio: {len(encrypted_bytes)} bytes -> {len(decrypted)} bytes")
            return decrypted
        except InvalidToken:
            logger.error("Decryption failed: invalid token (wrong key or corrupted data)")
            raise
        except Exception as e:
            logger.error(f"Audio decryption failed: {str(e)}")
            raise Exception(f"Decryption failed: {str(e)}")

    def rotate_key(self, old_key: str, new_key: str, encrypted_data: bytes) -> bytes:
        """
        Re-encrypt data with a new key (for key rotation).

        Args:
            old_key: Previous encryption key
            new_key: New encryption key
            encrypted_data: Data encrypted with old key

        Returns:
            Data re-encrypted with new key
        """
        old_cipher = Fernet(old_key.encode())
        new_cipher = Fernet(new_key.encode())

        # Decrypt with old key
        decrypted = old_cipher.decrypt(encrypted_data)

        # Encrypt with new key
        re_encrypted = new_cipher.encrypt(decrypted)

        logger.info("Successfully rotated encryption key")
        return re_encrypted

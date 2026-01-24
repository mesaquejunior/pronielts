"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    PROJECT_NAME: str = "PronIELTS API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Azure Services (optional in mock mode)
    MOCK_MODE: bool = True
    SPEECH_KEY: str | None = None
    SPEECH_REGION: str | None = "brazilsouth"
    BLOB_CONNECTION_STRING: str | None = None
    BLOB_CONTAINER_NAME: str = "audio-recordings"

    # Security
    ENCRYPTION_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS from comma-separated string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    def validate_azure_config(self) -> None:
        """Validate that Azure configuration is present when not in mock mode."""
        if not self.MOCK_MODE:
            if not self.SPEECH_KEY:
                raise ValueError("SPEECH_KEY is required when MOCK_MODE=false")
            if not self.BLOB_CONNECTION_STRING:
                raise ValueError("BLOB_CONNECTION_STRING is required when MOCK_MODE=false")


# Global settings instance
settings = Settings()

# Validate configuration on startup
if not settings.MOCK_MODE:
    settings.validate_azure_config()

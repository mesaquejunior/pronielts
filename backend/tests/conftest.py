"""
Test configuration and fixtures for PronIELTS backend tests.
Uses SQLite in-memory database for fast, isolated tests.
"""

import os

# Set environment variables before importing the app
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["ENCRYPTION_KEY"] = "xad7-9FTK2MR2M9jXPJ5wKEkhcLZ9uO9KVHGGfaH9c4="
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["MOCK_MODE"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.assessment import Assessment
from app.models.dialog import Dialog
from app.models.phrase import Phrase
from app.models.user import User

# In-memory SQLite engine for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a database session for direct model testing."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """Provide a FastAPI TestClient with overridden database dependency.

    Uses the same db session as the fixtures so committed data is visible
    to endpoint handlers.
    """

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ============================================================================
# Factory Fixtures
# ============================================================================


@pytest.fixture
def create_dialog(db):
    """Factory fixture for creating dialogs."""

    def _create_dialog(
        title="Test Dialog",
        category="IELTS_Part1",
        description="A test dialog for unit testing",
        difficulty_level="Intermediate",
    ):
        dialog = Dialog(
            title=title,
            category=category,
            description=description,
            difficulty_level=difficulty_level,
        )
        db.add(dialog)
        db.commit()
        db.refresh(dialog)
        return dialog

    return _create_dialog


@pytest.fixture
def create_phrase(db):
    """Factory fixture for creating phrases."""

    def _create_phrase(
        dialog_id,
        reference_text="Hello, how are you today?",
        order=0,
        phonetic_transcription=None,
        difficulty="Intermediate",
    ):
        phrase = Phrase(
            dialog_id=dialog_id,
            reference_text=reference_text,
            order=order,
            phonetic_transcription=phonetic_transcription,
            difficulty=difficulty,
        )
        db.add(phrase)
        db.commit()
        db.refresh(phrase)
        return phrase

    return _create_phrase


@pytest.fixture
def create_user(db):
    """Factory fixture for creating users."""

    def _create_user(
        user_id="test-user-uuid-1234",
        email=None,
        full_name=None,
    ):
        user = User(
            user_id=user_id,
            email=email,
            full_name=full_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return _create_user


@pytest.fixture
def create_assessment(db):
    """Factory fixture for creating assessments."""

    def _create_assessment(
        user_id,
        phrase_id,
        accuracy_score=85.0,
        prosody_score=4.0,
        fluency_score=80.0,
        completeness_score=90.0,
        overall_score=85.0,
        recognized_text="Hello, how are you today?",
        word_level_scores=None,
        audio_blob_url="local://test/audio.wav",
    ):
        assessment = Assessment(
            user_id=user_id,
            phrase_id=phrase_id,
            accuracy_score=accuracy_score,
            prosody_score=prosody_score,
            fluency_score=fluency_score,
            completeness_score=completeness_score,
            overall_score=overall_score,
            recognized_text=recognized_text,
            word_level_scores=word_level_scores or {},
            audio_blob_url=audio_blob_url,
            assessment_duration_seconds=2.5,
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment

    return _create_assessment


# ============================================================================
# Pre-built Data Fixtures
# ============================================================================


@pytest.fixture
def sample_dialog(create_dialog):
    """A pre-created dialog for tests that just need one."""
    return create_dialog()


@pytest.fixture
def sample_phrase(create_phrase, sample_dialog):
    """A pre-created phrase for tests that just need one."""
    return create_phrase(dialog_id=sample_dialog.id)


@pytest.fixture
def sample_user(create_user):
    """A pre-created user for tests that just need one."""
    return create_user()


@pytest.fixture
def sample_assessment(create_assessment, sample_user, sample_phrase):
    """A pre-created assessment for tests that just need one."""
    return create_assessment(
        user_id=sample_user.id,
        phrase_id=sample_phrase.id,
    )


@pytest.fixture
def wav_audio_bytes():
    """Minimal valid WAV file bytes for testing audio upload."""
    # Minimal WAV header (44 bytes) + 1 second of silence at 16kHz mono 16-bit
    import struct

    sample_rate = 16000
    num_channels = 1
    bits_per_sample = 16
    num_samples = sample_rate  # 1 second
    data_size = num_samples * num_channels * (bits_per_sample // 8)

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,  # ChunkSize
        b"WAVE",
        b"fmt ",
        16,  # Subchunk1Size (PCM)
        1,  # AudioFormat (PCM)
        num_channels,
        sample_rate,
        sample_rate * num_channels * (bits_per_sample // 8),  # ByteRate
        num_channels * (bits_per_sample // 8),  # BlockAlign
        bits_per_sample,
        b"data",
        data_size,
    )
    # Silence data
    audio_data = b"\x00\x00" * num_samples
    return header + audio_data

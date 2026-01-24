"""Assessment model for storing pronunciation evaluation results."""
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class Assessment(Base, TimestampMixin):
    """
    Assessment model storing pronunciation evaluation results.

    Stores scores from Azure Speech SDK (or mock) including:
    - Overall metrics (accuracy, prosody, fluency, completeness)
    - Detailed word-level and phoneme-level scores
    - Audio file reference (encrypted in blob storage)
    """

    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    phrase_id = Column(
        Integer,
        ForeignKey("phrases.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Scores (0-100 scale, except prosody which is 0-5)
    accuracy_score = Column(Float, nullable=True)  # Phoneme/word accuracy
    prosody_score = Column(Float, nullable=True)  # Rhythm/intonation (0-5)
    fluency_score = Column(Float, nullable=True)  # Speaking pace
    completeness_score = Column(Float, nullable=True)  # % of reference text
    overall_score = Column(Float, nullable=True, index=True)  # Aggregated score

    # Detailed results (stored as JSON)
    word_level_scores = Column(JSON, nullable=True)  # {"word": {"accuracy": 85, "error_type": "None"}}
    phoneme_level_scores = Column(JSON, nullable=True)  # Detailed phoneme scores (optional)
    recognized_text = Column(Text, nullable=True)  # Speech-to-text result

    # Metadata
    audio_blob_url = Column(String(500), nullable=True)  # Encrypted audio in blob storage
    assessment_duration_seconds = Column(Float, nullable=True)  # Audio duration

    # Relationships
    user = relationship("User")
    phrase = relationship("Phrase", back_populates="assessments")

    def __repr__(self) -> str:
        return f"<Assessment(id={self.id}, user_id={self.user_id}, overall_score={self.overall_score})>"

    def to_dict(self) -> dict:
        """Convert assessment to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "phrase_id": self.phrase_id,
            "scores": {
                "accuracy_score": self.accuracy_score,
                "prosody_score": self.prosody_score,
                "fluency_score": self.fluency_score,
                "completeness_score": self.completeness_score,
                "overall_score": self.overall_score
            },
            "recognized_text": self.recognized_text,
            "word_level_scores": self.word_level_scores,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

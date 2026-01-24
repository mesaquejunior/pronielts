"""Phrase model for individual sentences to practice."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Phrase(Base):
    """
    Phrase model representing individual practice sentences.

    Each phrase belongs to a dialog and can have multiple assessments
    from different users.
    """

    __tablename__ = "phrases"

    id = Column(Integer, primary_key=True, index=True)
    dialog_id = Column(
        Integer,
        ForeignKey("dialogs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    reference_text = Column(Text, nullable=False)
    order = Column(Integer, default=0, nullable=False)  # Display order within dialog
    phonetic_transcription = Column(Text, nullable=True)  # IPA transcription (optional)
    difficulty = Column(String(50), default="Intermediate", nullable=False)

    # Relationships
    dialog = relationship("Dialog", back_populates="phrases")
    assessments = relationship(
        "Assessment",
        back_populates="phrase",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        preview = self.reference_text[:50] + "..." if len(self.reference_text) > 50 else self.reference_text
        return f"<Phrase(id={self.id}, text='{preview}')>"

"""Dialog model for grouping related phrases by theme."""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Dialog(Base, TimestampMixin):
    """
    Dialog model representing themed conversation contexts.

    Categories:
    - Professional: Work-related scenarios
    - Travel: Airport, hotel, directions
    - General: Daily conversation
    - Restaurant: Dining situations
    - IELTS_Part1: Personal information questions
    - IELTS_Part2: Long turn (2-minute talk)
    - IELTS_Part3: Discussion topics
    """

    __tablename__ = "dialogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    difficulty_level = Column(String(50), default="Intermediate", nullable=False)

    # Relationships
    phrases = relationship(
        "Phrase",
        back_populates="dialog",
        cascade="all, delete-orphan",  # Delete phrases when dialog is deleted
        lazy="select",  # Load phrases only when accessed
    )

    def __repr__(self) -> str:
        return f"<Dialog(id={self.id}, title={self.title}, category={self.category})>"

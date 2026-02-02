"""Dialog model for grouping related phrases by theme."""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Dialog(Base, TimestampMixin):
    """
    Dialog model representing themed conversation contexts.

    Categories are managed via the Category model and linked by category_id FK.
    """

    __tablename__ = "dialogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description = Column(Text, nullable=True)
    difficulty_level = Column(String(50), default="Intermediate", nullable=False)

    # Relationships
    category_rel = relationship("Category", back_populates="dialogs")
    phrases = relationship(
        "Phrase",
        back_populates="dialog",
        cascade="all, delete-orphan",  # Delete phrases when dialog is deleted
        lazy="select",  # Load phrases only when accessed
    )

    @property
    def category_name(self) -> str:
        """Return the category name for serialization."""
        return self.category_rel.name if self.category_rel else ""

    def __repr__(self) -> str:
        return f"<Dialog(id={self.id}, title={self.title}, category_id={self.category_id})>"

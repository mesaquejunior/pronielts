"""Category model for organizing dialogs by theme."""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """
    Category model representing dialog themes/groupings.

    Examples: Professional, Travel, General, Restaurant,
    IELTS_Part1, IELTS_Part2, IELTS_Part3
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    dialogs = relationship(
        "Dialog",
        back_populates="category_rel",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name})>"

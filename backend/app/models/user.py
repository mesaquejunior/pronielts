"""User model for storing user information."""
from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    User model representing app users.

    For MVP: Users are identified by anonymous UUID (user_id).
    Future: Add authentication with email and password.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)  # Anonymous UUID
    email = Column(String(255), unique=True, nullable=True)  # Optional for future use
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, user_id={self.user_id})>"

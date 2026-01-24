"""Pydantic schemas for user-related requests and responses."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema (shared fields)."""

    email: EmailStr | None = None
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    user_id: str  # Anonymous UUID from mobile


class UserResponse(UserBase):
    """Response schema for user."""

    id: int
    user_id: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProgress(BaseModel):
    """User progress statistics."""

    user_id: int
    total_assessments: int
    average_overall_score: float
    average_accuracy: float
    average_prosody: float
    average_fluency: float
    average_completeness: float
    best_score: float
    worst_score: float
    categories_practiced: dict
    improvement_rate: float | None = None

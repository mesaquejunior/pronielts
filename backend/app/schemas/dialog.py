"""Pydantic schemas for dialog-related requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class PhraseBase(BaseModel):
    """Base phrase schema (shared fields)."""

    reference_text: str = Field(..., min_length=1, max_length=1000)
    order: int = Field(default=0, ge=0)
    phonetic_transcription: str | None = None
    difficulty: str = Field(default="Intermediate")


class PhraseResponse(PhraseBase):
    """Response schema for phrase."""

    id: int
    dialog_id: int

    model_config = {"from_attributes": True}


class DialogBase(BaseModel):
    """Base dialog schema (shared fields)."""

    title: str = Field(..., min_length=1, max_length=255)
    category_id: int = Field(..., description="Category ID (FK to categories)")
    description: str | None = None
    difficulty_level: str = Field(default="Intermediate")


class DialogCreate(DialogBase):
    """Schema for creating a new dialog."""


class DialogUpdate(BaseModel):
    """Schema for updating a dialog (all fields optional)."""

    title: str | None = Field(None, min_length=1, max_length=255)
    category_id: int | None = None
    description: str | None = None
    difficulty_level: str | None = None


class DialogResponse(BaseModel):
    """Response schema for dialog with phrases."""

    id: int
    title: str
    category_id: int
    category_name: str = Field(..., description="Category name for display")
    description: str | None = None
    difficulty_level: str
    created_at: datetime
    updated_at: datetime | None = None
    phrases: list[PhraseResponse] = []

    model_config = {"from_attributes": True}


class DialogListItem(BaseModel):
    """Simplified dialog for list responses (without phrases)."""

    id: int
    title: str
    category_id: int
    category_name: str
    description: str | None = None
    difficulty_level: str
    created_at: datetime
    phrase_count: int | None = 0

    model_config = {"from_attributes": True}

"""Pydantic schemas for phrase-related requests and responses."""
from typing import Optional
from pydantic import BaseModel, Field


class PhraseCreate(BaseModel):
    """Schema for creating a new phrase."""
    dialog_id: int = Field(..., gt=0)
    reference_text: str = Field(..., min_length=1, max_length=1000)
    order: int = Field(default=0, ge=0)
    phonetic_transcription: Optional[str] = None
    difficulty: str = Field(default="Intermediate")


class PhraseUpdate(BaseModel):
    """Schema for updating a phrase (all fields optional)."""
    reference_text: Optional[str] = Field(None, min_length=1, max_length=1000)
    order: Optional[int] = Field(None, ge=0)
    phonetic_transcription: Optional[str] = None
    difficulty: Optional[str] = None


class PhraseResponse(BaseModel):
    """Response schema for phrase."""
    id: int
    dialog_id: int
    reference_text: str
    order: int
    phonetic_transcription: Optional[str]
    difficulty: str

    model_config = {"from_attributes": True}

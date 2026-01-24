"""Pydantic schemas for assessment-related requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AssessmentScores(BaseModel):
    """Scores from pronunciation assessment."""

    accuracy_score: float = Field(..., ge=0, le=100, description="Phoneme/word accuracy (0-100)")
    prosody_score: float = Field(..., ge=0, le=5, description="Rhythm/intonation (0-5)")
    fluency_score: float = Field(..., ge=0, le=100, description="Speaking pace (0-100)")
    completeness_score: float = Field(..., ge=0, le=100, description="% of reference text (0-100)")
    overall_score: float = Field(..., ge=0, le=100, description="Aggregated score (0-100)")


class AssessmentCreate(BaseModel):
    """Schema for creating a new assessment (not used directly, multipart form used)."""

    user_id: str = Field(..., description="Anonymous user identifier (UUID)")
    phrase_id: int = Field(..., gt=0, description="Phrase ID being assessed")


class AssessmentResponse(BaseModel):
    """Response schema for assessment results."""

    id: int
    user_id: int
    phrase_id: int
    scores: AssessmentScores
    recognized_text: str | None = None
    word_level_scores: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AssessmentListItem(BaseModel):
    """Simplified assessment for list responses."""

    id: int
    phrase_id: int
    phrase_text: str
    overall_score: float
    accuracy_score: float
    prosody_score: float
    fluency_score: float
    created_at: datetime

    model_config = {"from_attributes": True}

"""User endpoints for managing users and viewing progress."""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db
from app.models.user import User
from app.models.assessment import Assessment
from app.models.phrase import Phrase
from app.models.dialog import Dialog
from app.schemas.user import UserResponse, UserProgress
from app.schemas.assessment import AssessmentListItem

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/users/{user_id}/assessments", response_model=List[AssessmentListItem])
def get_user_assessments(
    user_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get assessment history for a specific user.

    Returns assessments ordered by creation date (newest first).
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # Query assessments with phrase info
    assessments = (
        db.query(Assessment, Phrase.reference_text)
        .join(Phrase, Assessment.phrase_id == Phrase.id)
        .filter(Assessment.user_id == user_id)
        .order_by(Assessment.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    result = [
        AssessmentListItem(
            id=assessment.id,
            phrase_id=assessment.phrase_id,
            phrase_text=phrase_text,
            overall_score=assessment.overall_score,
            accuracy_score=assessment.accuracy_score,
            prosody_score=assessment.prosody_score,
            fluency_score=assessment.fluency_score,
            created_at=assessment.created_at
        )
        for assessment, phrase_text in assessments
    ]

    logger.info(f"Retrieved {len(result)} assessments for user {user_id}")
    return result


@router.get("/users/{user_id}/progress", response_model=UserProgress)
def get_user_progress(user_id: int, db: Session = Depends(get_db)):
    """
    Get aggregated progress statistics for a user.

    Includes:
    - Total assessments
    - Average scores (overall, accuracy, prosody, fluency, completeness)
    - Best and worst scores
    - Category breakdown
    - Improvement rate (future enhancement)
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # Get aggregated statistics
    stats = (
        db.query(
            func.count(Assessment.id).label("total"),
            func.avg(Assessment.overall_score).label("avg_overall"),
            func.avg(Assessment.accuracy_score).label("avg_accuracy"),
            func.avg(Assessment.prosody_score).label("avg_prosody"),
            func.avg(Assessment.fluency_score).label("avg_fluency"),
            func.avg(Assessment.completeness_score).label("avg_completeness"),
            func.max(Assessment.overall_score).label("best_score"),
            func.min(Assessment.overall_score).label("worst_score")
        )
        .filter(Assessment.user_id == user_id)
        .first()
    )

    # Get category breakdown
    category_counts = (
        db.query(Dialog.category, func.count(Assessment.id).label("count"))
        .join(Phrase, Assessment.phrase_id == Phrase.id)
        .join(Dialog, Phrase.dialog_id == Dialog.id)
        .filter(Assessment.user_id == user_id)
        .group_by(Dialog.category)
        .all()
    )

    categories_practiced = {category: count for category, count in category_counts}

    # Handle case where user has no assessments
    if stats.total == 0:
        return UserProgress(
            user_id=user_id,
            total_assessments=0,
            average_overall_score=0.0,
            average_accuracy=0.0,
            average_prosody=0.0,
            average_fluency=0.0,
            average_completeness=0.0,
            best_score=0.0,
            worst_score=0.0,
            categories_practiced={},
            improvement_rate=None
        )

    logger.info(f"Retrieved progress for user {user_id}: {stats.total} assessments")

    return UserProgress(
        user_id=user_id,
        total_assessments=stats.total,
        average_overall_score=float(stats.avg_overall or 0),
        average_accuracy=float(stats.avg_accuracy or 0),
        average_prosody=float(stats.avg_prosody or 0),
        average_fluency=float(stats.avg_fluency or 0),
        average_completeness=float(stats.avg_completeness or 0),
        best_score=float(stats.best_score or 0),
        worst_score=float(stats.worst_score or 0),
        categories_practiced=categories_practiced,
        improvement_rate=None  # TODO: Calculate based on time series data
    )

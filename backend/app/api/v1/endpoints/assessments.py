"""
Assessment endpoints for pronunciation evaluation.
Main endpoint: POST /assess - submits audio for assessment.
"""

import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_blob_service, get_db, get_encryption_service, get_speech_service
from app.models.assessment import Assessment
from app.models.phrase import Phrase
from app.models.user import User
from app.schemas.assessment import AssessmentResponse, AssessmentScores
from app.services.blob_service import BlobStorageService
from app.services.encryption_service import EncryptionService
from app.services.speech_service import SpeechAssessmentService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/assess", response_model=AssessmentResponse, status_code=200)
async def create_assessment(
    audio: UploadFile = File(..., description="Audio file (WAV format, max 10MB)"),
    phrase_id: int = Form(..., description="ID of phrase being assessed"),
    user_id: str = Form(..., description="Anonymous user identifier (UUID)"),
    db: Session = Depends(get_db),
    speech_service: SpeechAssessmentService = Depends(get_speech_service),
    blob_service: BlobStorageService = Depends(get_blob_service),
    encryption_service: EncryptionService = Depends(get_encryption_service),
):
    """
    Submit audio for pronunciation assessment.

    Process:
    1. Validate audio file (size, format)
    2. Get or create user
    3. Fetch phrase from database
    4. Assess pronunciation using Azure Speech SDK (or mock)
    5. Encrypt audio file
    6. Upload encrypted audio to blob storage
    7. Save assessment results to database
    8. Return scores and feedback

    Returns:
        Assessment results with scores and word-level feedback
    """

    # 1. Validate audio file
    if audio.size and audio.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="Audio file too large (maximum 10MB)")

    if audio.content_type and audio.content_type not in ["audio/wav", "audio/wave", "audio/x-wav"]:
        logger.warning(f"Unexpected content type: {audio.content_type}. Proceeding anyway.")

    # 2. Get or create user
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        logger.info(f"Creating new user: {user_id}")
        user = User(user_id=user_id)
        db.add(user)
        db.flush()  # Get user.id without committing

    # 3. Get phrase
    phrase = db.query(Phrase).filter(Phrase.id == phrase_id).first()
    if not phrase:
        raise HTTPException(status_code=404, detail=f"Phrase with ID {phrase_id} not found")

    # 4. Read audio bytes
    audio_bytes = await audio.read()
    logger.info(f"Received audio: {len(audio_bytes)} bytes for phrase_id={phrase_id}")

    try:
        # 5. Assess pronunciation
        logger.info("Starting pronunciation assessment...")
        result = await speech_service.assess_pronunciation(audio_bytes, phrase.reference_text)

        logger.info(
            f"Assessment complete: accuracy={result.accuracy_score:.1f}, "
            f"prosody={result.prosody_score:.1f}, overall={result.overall_score:.1f}"
        )

        # 6. Encrypt audio
        logger.info("Encrypting audio...")
        encrypted_audio = encryption_service.encrypt_audio(audio_bytes)

        # 7. Upload to blob storage
        logger.info("Uploading to blob storage...")
        blob_url = await blob_service.upload_audio(
            encrypted_audio, file_extension="wav", user_id=user_id
        )

        # 8. Save assessment to database
        assessment = Assessment(
            user_id=user.id,
            phrase_id=phrase_id,
            accuracy_score=result.accuracy_score,
            prosody_score=result.prosody_score,
            fluency_score=result.fluency_score,
            completeness_score=result.completeness_score,
            overall_score=result.overall_score,
            recognized_text=result.recognized_text,
            word_level_scores=result.word_level_scores,
            audio_blob_url=blob_url,
            assessment_duration_seconds=len(audio_bytes) / 16000,  # Approximate duration
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        logger.info(f"Assessment saved: id={assessment.id}")

        # 9. Return response
        return AssessmentResponse(
            id=assessment.id,
            user_id=assessment.user_id,
            phrase_id=assessment.phrase_id,
            scores=AssessmentScores(
                accuracy_score=assessment.accuracy_score,
                prosody_score=assessment.prosody_score,
                fluency_score=assessment.fluency_score,
                completeness_score=assessment.completeness_score,
                overall_score=assessment.overall_score,
            ),
            recognized_text=assessment.recognized_text,
            word_level_scores=assessment.word_level_scores,
            created_at=assessment.created_at,
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Assessment failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")

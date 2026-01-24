"""Phrase endpoints for managing practice sentences."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.dialog import Dialog
from app.models.phrase import Phrase
from app.schemas.phrase import PhraseCreate, PhraseResponse, PhraseUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/phrases/{phrase_id}", response_model=PhraseResponse)
def get_phrase(phrase_id: int, db: Session = Depends(get_db)):
    """Get a specific phrase by ID."""
    phrase = db.query(Phrase).filter(Phrase.id == phrase_id).first()

    if not phrase:
        raise HTTPException(status_code=404, detail=f"Phrase {phrase_id} not found")

    return phrase


@router.post("/phrases", response_model=PhraseResponse, status_code=201)
def create_phrase(phrase: PhraseCreate, db: Session = Depends(get_db)):
    """
    Create a new phrase (Admin only).

    The phrase will be added to the specified dialog.
    """
    # Verify dialog exists
    dialog = db.query(Dialog).filter(Dialog.id == phrase.dialog_id).first()
    if not dialog:
        raise HTTPException(status_code=404, detail=f"Dialog {phrase.dialog_id} not found")

    db_phrase = Phrase(**phrase.model_dump())

    db.add(db_phrase)
    db.commit()
    db.refresh(db_phrase)

    logger.info(f"Created phrase: {db_phrase.reference_text[:50]}... (id={db_phrase.id})")
    return db_phrase


@router.put("/phrases/{phrase_id}", response_model=PhraseResponse)
def update_phrase(phrase_id: int, phrase_update: PhraseUpdate, db: Session = Depends(get_db)):
    """
    Update an existing phrase (Admin only).

    All fields are optional - only provided fields will be updated.
    """
    db_phrase = db.query(Phrase).filter(Phrase.id == phrase_id).first()

    if not db_phrase:
        raise HTTPException(status_code=404, detail=f"Phrase {phrase_id} not found")

    # Update only provided fields
    update_data = phrase_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_phrase, field, value)

    db.commit()
    db.refresh(db_phrase)

    logger.info(f"Updated phrase (id={phrase_id})")
    return db_phrase


@router.delete("/phrases/{phrase_id}", status_code=204)
def delete_phrase(phrase_id: int, db: Session = Depends(get_db)):
    """
    Delete a phrase (Admin only).

    WARNING: This will cascade delete all assessments for this phrase.
    """
    db_phrase = db.query(Phrase).filter(Phrase.id == phrase_id).first()

    if not db_phrase:
        raise HTTPException(status_code=404, detail=f"Phrase {phrase_id} not found")

    db.delete(db_phrase)
    db.commit()

    logger.info(f"Deleted phrase (id={phrase_id})")
    return None

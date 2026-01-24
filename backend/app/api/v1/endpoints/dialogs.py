"""Dialog endpoints for managing conversation contexts."""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.dialog import Dialog
from app.models.phrase import Phrase
from app.schemas.dialog import DialogCreate, DialogUpdate, DialogResponse, DialogListItem

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dialogs", response_model=List[DialogResponse])
def get_dialogs(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Get all dialogs, optionally filtered by category.

    Categories:
    - Professional
    - Travel
    - General
    - Restaurant
    - IELTS_Part1
    - IELTS_Part2
    - IELTS_Part3
    """
    query = db.query(Dialog)

    if category:
        query = query.filter(Dialog.category == category)

    dialogs = query.all()
    logger.info(f"Retrieved {len(dialogs)} dialogs (category={category})")

    return dialogs


@router.get("/dialogs/{dialog_id}", response_model=DialogResponse)
def get_dialog(dialog_id: int, db: Session = Depends(get_db)):
    """Get a specific dialog with all its phrases."""
    dialog = db.query(Dialog).filter(Dialog.id == dialog_id).first()

    if not dialog:
        raise HTTPException(status_code=404, detail=f"Dialog {dialog_id} not found")

    logger.info(f"Retrieved dialog: {dialog.title} with {len(dialog.phrases)} phrases")
    return dialog


@router.post("/dialogs", response_model=DialogResponse, status_code=201)
def create_dialog(
    dialog: DialogCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new dialog (Admin only - authentication to be added).

    Creates a new conversation context for practice.
    """
    db_dialog = Dialog(**dialog.model_dump())

    db.add(db_dialog)
    db.commit()
    db.refresh(db_dialog)

    logger.info(f"Created dialog: {db_dialog.title} (id={db_dialog.id})")
    return db_dialog


@router.put("/dialogs/{dialog_id}", response_model=DialogResponse)
def update_dialog(
    dialog_id: int,
    dialog_update: DialogUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing dialog (Admin only).

    All fields are optional - only provided fields will be updated.
    """
    db_dialog = db.query(Dialog).filter(Dialog.id == dialog_id).first()

    if not db_dialog:
        raise HTTPException(status_code=404, detail=f"Dialog {dialog_id} not found")

    # Update only provided fields
    update_data = dialog_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dialog, field, value)

    db.commit()
    db.refresh(db_dialog)

    logger.info(f"Updated dialog: {db_dialog.title} (id={db_dialog.id})")
    return db_dialog


@router.delete("/dialogs/{dialog_id}", status_code=204)
def delete_dialog(dialog_id: int, db: Session = Depends(get_db)):
    """
    Delete a dialog and all its phrases (Admin only).

    WARNING: This will cascade delete all phrases and assessments.
    """
    db_dialog = db.query(Dialog).filter(Dialog.id == dialog_id).first()

    if not db_dialog:
        raise HTTPException(status_code=404, detail=f"Dialog {dialog_id} not found")

    db.delete(db_dialog)
    db.commit()

    logger.info(f"Deleted dialog: {db_dialog.title} (id={dialog_id})")
    return None

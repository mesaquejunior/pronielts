"""Dialog endpoints for managing conversation contexts."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.category import Category
from app.models.dialog import Dialog
from app.schemas.dialog import DialogCreate, DialogResponse, DialogUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dialogs", response_model=list[DialogResponse])
def get_dialogs(
    category_id: int | None = Query(None, description="Filter by category ID"),
    category: str | None = Query(None, description="Filter by category name (for backward compatibility)"),
    db: Session = Depends(get_db),
):
    """
    Get all dialogs, optionally filtered by category.

    Use GET /categories to get the list of available categories.
    Supports filtering by either category_id or category name.
    """
    query = db.query(Dialog).options(joinedload(Dialog.category_rel))

    if category_id:
        query = query.filter(Dialog.category_id == category_id)
    elif category:
        query = query.join(Category).filter(Category.name == category)

    dialogs = query.all()
    logger.info(f"Retrieved {len(dialogs)} dialogs (category_id={category_id}, category={category})")

    return dialogs


@router.get("/dialogs/{dialog_id}", response_model=DialogResponse)
def get_dialog(dialog_id: int, db: Session = Depends(get_db)):
    """Get a specific dialog with all its phrases."""
    dialog = (
        db.query(Dialog)
        .options(joinedload(Dialog.category_rel))
        .filter(Dialog.id == dialog_id)
        .first()
    )

    if not dialog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dialog {dialog_id} not found",
        )

    logger.info(f"Retrieved dialog: {dialog.title} with {len(dialog.phrases)} phrases")
    return dialog


@router.post("/dialogs", response_model=DialogResponse, status_code=status.HTTP_201_CREATED)
def create_dialog(dialog: DialogCreate, db: Session = Depends(get_db)):
    """
    Create a new dialog (Admin only - authentication to be added).

    Creates a new conversation context for practice.
    Requires a valid category_id.
    """
    # Validate category exists
    category = db.query(Category).filter(Category.id == dialog.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {dialog.category_id} not found",
        )

    db_dialog = Dialog(**dialog.model_dump())

    db.add(db_dialog)
    db.commit()
    db.refresh(db_dialog)

    logger.info(f"Created dialog: {db_dialog.title} (id={db_dialog.id})")
    return db_dialog


@router.put("/dialogs/{dialog_id}", response_model=DialogResponse)
def update_dialog(dialog_id: int, dialog_update: DialogUpdate, db: Session = Depends(get_db)):
    """
    Update an existing dialog (Admin only).

    All fields are optional - only provided fields will be updated.
    """
    db_dialog = (
        db.query(Dialog)
        .options(joinedload(Dialog.category_rel))
        .filter(Dialog.id == dialog_id)
        .first()
    )

    if not db_dialog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dialog {dialog_id} not found",
        )

    # Update only provided fields
    update_data = dialog_update.model_dump(exclude_unset=True)

    # Validate category_id if being updated
    if "category_id" in update_data:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category {update_data['category_id']} not found",
            )

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

"""Category endpoints for managing dialog categories."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """
    Get all categories with dialog counts.

    Returns a list of all categories ordered by name.
    """
    categories = db.query(Category).order_by(Category.name).all()

    # Build response with dialog counts
    result = []
    for cat in categories:
        response = CategoryResponse(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            created_at=cat.created_at,
            updated_at=cat.updated_at,
            dialog_count=len(cat.dialogs),
        )
        result.append(response)

    return result


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category by ID."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found",
        )

    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        created_at=category.created_at,
        updated_at=category.updated_at,
        dialog_count=len(category.dialogs),
    )


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """
    Create a new category.

    Returns 409 Conflict if a category with the same name already exists.
    """
    # Check uniqueness
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{category.name}' already exists",
        )

    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    logger.info(f"Created category: {db_category.name} (id={db_category.id})")

    return CategoryResponse(
        id=db_category.id,
        name=db_category.name,
        description=db_category.description,
        created_at=db_category.created_at,
        updated_at=db_category.updated_at,
        dialog_count=0,
    )


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing category."""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found",
        )

    update_data = category_update.model_dump(exclude_unset=True)

    # Check name uniqueness if updating name
    if "name" in update_data:
        existing = (
            db.query(Category)
            .filter(Category.name == update_data["name"], Category.id != category_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Category '{update_data['name']}' already exists",
            )

    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)

    logger.info(f"Updated category: {db_category.name} (id={category_id})")

    return CategoryResponse(
        id=db_category.id,
        name=db_category.name,
        description=db_category.description,
        created_at=db_category.created_at,
        updated_at=db_category.updated_at,
        dialog_count=len(db_category.dialogs),
    )


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Delete a category and ALL its dialogs (cascade).

    WARNING: This will delete all dialogs, phrases, and assessments
    under this category due to cascade delete.
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {category_id} not found",
        )

    category_name = db_category.name
    dialog_count = len(db_category.dialogs)

    db.delete(db_category)
    db.commit()

    logger.info(
        f"Deleted category: {category_name} (id={category_id}) "
        f"with {dialog_count} dialogs (cascade)"
    )

    return None

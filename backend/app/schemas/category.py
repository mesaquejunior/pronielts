"""Pydantic schemas for category-related requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category schema with shared fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: str | None = Field(None, description="Category description")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category (all fields optional)."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class CategoryResponse(CategoryBase):
    """Response schema for category."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None
    dialog_count: int = 0

    model_config = {"from_attributes": True}

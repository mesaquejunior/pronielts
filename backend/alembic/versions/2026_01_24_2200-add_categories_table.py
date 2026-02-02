"""Add categories table and convert dialog.category to FK.

Revision ID: a1b2c3d4e5f6
Revises: e1dcb526f75f
Create Date: 2026-01-24 22:00:00.000000

This migration:
1. Creates the categories table
2. Populates it with existing unique categories from dialogs
3. Adds category_id FK to dialogs and backfills from category names
4. Drops the old category string column
"""

from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "e1dcb526f75f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PHASE 1: Create the categories table
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)
    op.create_index(op.f("ix_categories_name"), "categories", ["name"], unique=True)

    # PHASE 2: Populate categories from existing dialog.category values
    # and add category_id column (nullable initially)
    op.add_column("dialogs", sa.Column("category_id", sa.Integer(), nullable=True))

    # Use raw SQL to:
    # 1) Insert distinct categories from dialogs
    # 2) Backfill category_id based on the category name
    conn = op.get_bind()
    conn.execute(
        sa.text("""
            INSERT INTO categories (name, created_at)
            SELECT DISTINCT category, NOW()
            FROM dialogs
            WHERE category IS NOT NULL
        """)
    )
    conn.execute(
        sa.text("""
            UPDATE dialogs
            SET category_id = categories.id
            FROM categories
            WHERE dialogs.category = categories.name
        """)
    )

    # PHASE 3: Make category_id NOT NULL, add FK, drop old column
    op.alter_column("dialogs", "category_id", nullable=False)
    op.create_foreign_key(
        "fk_dialogs_category_id_categories",
        "dialogs",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(op.f("ix_dialogs_category_id"), "dialogs", ["category_id"], unique=False)

    # Drop old string column and its index
    op.drop_index(op.f("ix_dialogs_category"), table_name="dialogs")
    op.drop_column("dialogs", "category")


def downgrade() -> None:
    # Reverse: re-add category string, populate from FK, drop FK and table
    op.add_column(
        "dialogs", sa.Column("category", sa.String(length=100), nullable=True)
    )

    conn = op.get_bind()
    conn.execute(
        sa.text("""
            UPDATE dialogs
            SET category = categories.name
            FROM categories
            WHERE dialogs.category_id = categories.id
        """)
    )

    op.alter_column("dialogs", "category", nullable=False)
    op.create_index(op.f("ix_dialogs_category"), "dialogs", ["category"], unique=False)

    op.drop_index(op.f("ix_dialogs_category_id"), table_name="dialogs")
    op.drop_constraint("fk_dialogs_category_id_categories", "dialogs", type_="foreignkey")
    op.drop_column("dialogs", "category_id")

    op.drop_index(op.f("ix_categories_name"), table_name="categories")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")

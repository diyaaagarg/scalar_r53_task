"""initial schema

Revision ID: 20261007_0001
Revises:
Create Date: 2026-10-07
"""
from alembic import op
from app.core.database import Base
import app.models.entities  # noqa: F401

revision = "20261007_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    Base.metadata.create_all(op.get_bind())

def downgrade() -> None:
    Base.metadata.drop_all(op.get_bind())

"""create checks table

Revision ID: 0001
Revises:
Create Date: 2026-07-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "checks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("program", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("issues", sa.JSON(), nullable=False),
        sa.Column("documents", sa.JSON(), nullable=False),
        sa.Column("extracted", sa.JSON(), nullable=False),
        sa.Column("checked_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("checks")
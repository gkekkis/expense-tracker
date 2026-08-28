"""add user password hash

Revision ID: f8a1c2b3d4e5
Revises: c4d9f2a1b730
Create Date: 2026-06-30 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f8a1c2b3d4e5"
down_revision: Union[str, Sequence[str], None] = "c4d9f2a1b730"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def upgrade() -> None:
    """Upgrade schema."""
    if not _has_column("users", "password_hash"):
        op.add_column("users", sa.Column("password_hash", sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    if _has_column("users", "password_hash"):
        op.drop_column("users", "password_hash")

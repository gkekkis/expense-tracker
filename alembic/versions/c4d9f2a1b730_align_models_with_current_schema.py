"""align models with current schema

Revision ID: c4d9f2a1b730
Revises: 8926f65b9f8a
Create Date: 2026-06-29 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4d9f2a1b730"
down_revision: Union[str, Sequence[str], None] = "8926f65b9f8a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return inspector.has_table(table_name)


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _has_index(table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def _has_foreign_key(table_name: str, constraint_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(foreign_key["name"] == constraint_name for foreign_key in inspector.get_foreign_keys(table_name))


def upgrade() -> None:
    """Upgrade schema to match the current SQLAlchemy models."""
    currency_enum = postgresql.ENUM(name="currency", create_type=False)

    if not _has_column("memberships", "default_contribution_share"):
        op.add_column(
            "memberships",
            sa.Column("default_contribution_share", sa.Numeric(3, 2), nullable=False, server_default="1.00"),
        )
        op.alter_column("memberships", "default_contribution_share", server_default=None)

    op.alter_column(
        "expenses", "amount", existing_type=sa.Numeric(10, 2), type_=sa.Numeric(12, 2), existing_nullable=False
    )
    if not _has_column("expenses", "global_event_id"):
        op.add_column("expenses", sa.Column("global_event_id", sa.UUID(), nullable=True))
    if not _has_column("expenses", "personal_responsibility_factor"):
        op.add_column("expenses", sa.Column("personal_responsibility_factor", sa.Numeric(3, 2), nullable=True))
    if not _has_column("expenses", "calculated_user_share"):
        op.add_column("expenses", sa.Column("calculated_user_share", sa.Numeric(12, 2), nullable=True))
    if not _has_index("expenses", op.f("ix_expenses_global_event_id")):
        op.create_index(op.f("ix_expenses_global_event_id"), "expenses", ["global_event_id"], unique=False)

    if not _has_column("recurring_templates", "created_by_user_id"):
        op.add_column("recurring_templates", sa.Column("created_by_user_id", sa.UUID(), nullable=True))
    if not _has_column("recurring_templates", "currency"):
        op.add_column("recurring_templates", sa.Column("currency", currency_enum, nullable=False, server_default="EUR"))
        op.alter_column("recurring_templates", "currency", server_default=None)
    if not _has_column("recurring_templates", "global_event_id"):
        op.add_column("recurring_templates", sa.Column("global_event_id", sa.UUID(), nullable=True))
    if not _has_column("recurring_templates", "personal_responsibility_factor"):
        op.add_column(
            "recurring_templates", sa.Column("personal_responsibility_factor", sa.Numeric(3, 2), nullable=True)
        )
    if not _has_foreign_key("recurring_templates", "fk_recurring_templates_created_by_user_id_users"):
        op.create_foreign_key(
            "fk_recurring_templates_created_by_user_id_users",
            "recurring_templates",
            "users",
            ["created_by_user_id"],
            ["id"],
        )
    if not _has_index("recurring_templates", op.f("ix_recurring_templates_global_event_id")):
        op.create_index(
            op.f("ix_recurring_templates_global_event_id"), "recurring_templates", ["global_event_id"], unique=False
        )

    if not _has_table("financial_profiles"):
        op.create_table(
            "financial_profiles",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("account_id", sa.UUID(), nullable=False),
            sa.Column("monthly_net_income", sa.Numeric(10, 2), nullable=True),
            sa.Column("savings_percentage_goal", sa.Numeric(5, 2), nullable=True),
            sa.Column("emergency_fund_target", sa.Numeric(10, 2), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("account_id"),
        )


def downgrade() -> None:
    """Downgrade schema."""
    if _has_table("financial_profiles"):
        op.drop_table("financial_profiles")

    if _has_index("recurring_templates", op.f("ix_recurring_templates_global_event_id")):
        op.drop_index(op.f("ix_recurring_templates_global_event_id"), table_name="recurring_templates")
    if _has_foreign_key("recurring_templates", "fk_recurring_templates_created_by_user_id_users"):
        op.drop_constraint("fk_recurring_templates_created_by_user_id_users", "recurring_templates", type_="foreignkey")
    if _has_column("recurring_templates", "personal_responsibility_factor"):
        op.drop_column("recurring_templates", "personal_responsibility_factor")
    if _has_column("recurring_templates", "global_event_id"):
        op.drop_column("recurring_templates", "global_event_id")
    if _has_column("recurring_templates", "currency"):
        op.drop_column("recurring_templates", "currency")
    if _has_column("recurring_templates", "created_by_user_id"):
        op.drop_column("recurring_templates", "created_by_user_id")

    if _has_index("expenses", op.f("ix_expenses_global_event_id")):
        op.drop_index(op.f("ix_expenses_global_event_id"), table_name="expenses")
    if _has_column("expenses", "calculated_user_share"):
        op.drop_column("expenses", "calculated_user_share")
    if _has_column("expenses", "personal_responsibility_factor"):
        op.drop_column("expenses", "personal_responsibility_factor")
    if _has_column("expenses", "global_event_id"):
        op.drop_column("expenses", "global_event_id")
    op.alter_column(
        "expenses", "amount", existing_type=sa.Numeric(12, 2), type_=sa.Numeric(10, 2), existing_nullable=False
    )

    if _has_column("memberships", "default_contribution_share"):
        op.drop_column("memberships", "default_contribution_share")

"""fix memberships accepted_at and user_id index

Revision ID: db4b51753971
Revises: f7c50b316be1
Create Date: 2026-11-16 17:24:27.107334

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "db4b51753971"
down_revision: str | Sequence[str] | None = "f7c50b316be1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("memberships", "accepted_by", new_column_name="accepted_at")
    op.create_index(op.f("ix_memberships_user_id"), "memberships", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_memberships_user_id"), table_name="memberships")
    op.alter_column("memberships", "accepted_at", new_column_name="accepted_by")

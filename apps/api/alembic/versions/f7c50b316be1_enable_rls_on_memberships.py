"""enable rls on memberships

Revision ID: f7c50b316be1
Revises: ac51b846539a
Create Date: 2026-11-16 17:11:23.274112

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f7c50b316be1"
down_revision: str | Sequence[str] | None = "ac51b846539a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE memberships ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE memberships FORCE ROW LEVEL SECURITY")

    op.execute("""
        CREATE POLICY tenant_isolation ON memberships
          USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
          WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
    """)

    op.execute("""
        CREATE POLICY own_memberships ON memberships
          FOR SELECT
          USING (user_id = NULLIF(current_setting('app.user_id', true), '')::uuid)
    """)


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS own_memberships ON memberships")
    op.execute("DROP POLICY IF EXISTS tenant_isolation ON memberships")
    op.execute("ALTER TABLE memberships NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE memberships DISABLE ROW LEVEL SECURITY")

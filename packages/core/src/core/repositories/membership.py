from uuid import UUID

from sqlalchemy import Row, exists, select
from sqlalchemy.orm import Session

from core.models import Membership, Tenant


class MembershipRepository:
    def __init__(self, session: Session):
        self.session = session

    def is_active_member(self, tenant_id: UUID, user_id: UUID) -> bool:
        return bool(
            self.session.scalar(
                select(
                    exists().where(
                        Membership.tenant_id == tenant_id,
                        Membership.user_id == user_id,
                        Membership.accepted_at.is_not(None),
                    )
                )
            )
        )

    def list_user_tenants(self, user_id: UUID) -> list[Row]:
        stmt = (
            select(Membership.tenant_id, Membership.role, Tenant.name, Tenant.slug)
            .join(Tenant, Tenant.id == Membership.tenant_id)
            .where(Membership.user_id == user_id, Membership.accepted_at.is_not(None))
            .order_by(Tenant.name)
        )

        return list(self.session.execute(stmt))

    def list_for_current_tenant(self) -> list[Membership]:
        return list(self.session.scalars(select(Membership).order_by(Membership.created_at)))

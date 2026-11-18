from uuid import UUID

from core.repositories import MembershipRepository, UserRepository
from sqlalchemy.orm import Session

from api.modules.me.schemas import MeOut, TenantAccessOut, UserOut


class UserNotFoundError(Exception):
    """O usuário do token não existe mais."""


def get_profile(session: Session, user_id: UUID) -> MeOut:
    user = UserRepository(session).get(user_id=user_id)

    if not user:
        raise UserNotFoundError

    rows = MembershipRepository(session).list_user_tenants(user_id=user_id)

    return MeOut(
        user=UserOut.model_validate(user),
        tenants=[
            TenantAccessOut(tenant_id=r.tenant_id, name=r.name, slug=r.slug, role=r.role)
            for r in rows
        ],
    )
